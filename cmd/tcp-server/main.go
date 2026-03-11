package main

import (
	"context"
	"encoding/gob"
	"log/slog"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/google/uuid"
	"github.com/saryginrodion/netmon/internal/collectors/activetcp"
)

const LISTEN_ADDR string = ":8001"

func main() {
	log := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
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

	enc := gob.NewEncoder(conn)
	dec := gob.NewDecoder(conn)

	for {
		request := &activetcp.TCPMessage{}
		err := dec.Decode(request)
		if err != nil {
			log.Warn("failed to read next line", "err", err)
			break
		}

		log.Info(
			"received message", 
			"message", request,
		)

		response := activetcp.TCPMessage{
			MessageID: uuid.New(),
			ReplyTo:   &request.MessageID,
			Timestamp: time.Now(),
			Data:      map[string]any{},
		}

		err = enc.Encode(response)
		if err != nil {
			log.Warn("failed to send ACK", "err", err)
			break
		}
	}
}
