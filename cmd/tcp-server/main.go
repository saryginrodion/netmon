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
)

const LISTEN_ADDR string = ":8001"

func main() {
	log := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))
	log.WithGroup("tcp-server")

	listener, err := net.Listen("tcp", LISTEN_ADDR)
	if err != nil {
		log.Error("unable to start listener", "err", err)
		os.Exit(1)
	}

	log.Debug("opened tcp listener", "addr", LISTEN_ADDR)

	// connection handling
	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		log := log.With("scope", "connectionHandleLoop")

		isRunning := true
		for {
			select {
			case <-ctx.Done():
				isRunning = false
			default:
			}

			if !isRunning {
				break
			}

			conn, err := listener.Accept()
			if err != nil {
				log.Error("failed to accept connection", "err", err)
				continue
			}

			go handleConn(log, conn)
		}
	}()

	// Graceful shutdown
	killSig := make(chan os.Signal, 1)
	signal.Notify(killSig, syscall.SIGINT, syscall.SIGTERM)

	<-killSig

	log.Debug("shutting down")
	cancel()

	if err := listener.Close(); err != nil {
		log.Error("listener closed with error", "err", err)
	}
}

func handleConn(logger *slog.Logger, conn net.Conn) {
	defer conn.Close()

	log := logger.With(
		"scope", "handleConn",
		"remoteAddr", conn.RemoteAddr(),
		"localAddr", conn.LocalAddr(),
	)

	log.Debug("starting connection handling")

	reader := bufio.NewReader(conn)

	for {
		s, err := reader.ReadString(byte('\n'))
		if err != nil {
			log.Warn("failed to read next line", "err", err)
			break
		}

		log.Info("received message", "message", s)

		_, err = fmt.Fprintf(conn, "ACK: %s", s)
		if err != nil {
			log.Warn("failed to send ACK", "err", err)
			break
		}
	}
}
