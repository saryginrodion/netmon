package activetcp

import (
	"time"

	"github.com/google/uuid"
)

type MessageID = uuid.UUID

type TCPMessage struct {
	MessageID      MessageID
	ReplyTo        *MessageID
	Timestamp      time.Time
	Data map[string]any
}
