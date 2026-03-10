package main

import (
	"bufio"
	"context"
	"fmt"
	"log/slog"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"
)

const CONNECTION_ADDR = "localhost:8001"
const PACKET_RATE = time.Second / 10

func main() {
	log := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))
	log.WithGroup("tcp-server")

	conn, err := net.Dial("tcp", CONNECTION_ADDR)
	if err != nil {
		log.Error("unable to dial TCP connection", "err", err)
		os.Exit(1)
	}

	log.Debug("opened tcp connection", "addr", CONNECTION_ADDR)

	// connection handling
	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		log := log.With("scope", "connectionHandleLoop")
		go handleConn(ctx, log, conn)
	}()

	// Graceful shutdown
	killSig := make(chan os.Signal, 1)
	signal.Notify(killSig, syscall.SIGINT, syscall.SIGTERM)

	<-killSig

	log.Debug("shutting down")
	cancel()

	if err := conn.Close(); err != nil {
		log.Error("listener closed with error", "err", err)
	}
}

func handleConn(ctx context.Context, logger *slog.Logger, conn net.Conn) {
	defer conn.Close()

	log := logger.With(
		"scope", "handleConn",
		"remoteAddr", conn.RemoteAddr(),
		"localAddr", conn.LocalAddr(),
	)

	log.Debug("starting connection handling")

	reader := bufio.NewReader(conn)

	isRunning := true

	ticker := time.NewTicker(PACKET_RATE)

	for range ticker.C {
		select {
		case <-ctx.Done():
			isRunning = false
		default:
		}

		if !isRunning {
			ticker.Stop()
			break
		}

		_, err := fmt.Fprintf(conn, "test message\n")
		if err != nil {
			log.Warn("failed to send message", "err", err)
			break
		}

		s, err := reader.ReadString(byte('\n'))
		if err != nil {
			log.Warn("failed to read response", "err", err)
			break
		}

		log.Info("received message", "message", s)
	}
}
