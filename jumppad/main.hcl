# Jumppad Configuration for Hugging Face Chat-UI with MongoDB
#
# Usage:
#   1. Set your OpenAI API key: export OPENAI_API_KEY=your_key_here
#   2. Run: jumppad up
#   3. Access chat-ui at: http://localhost:3000
#
# To tear down: jumppad down

# Create a network for container communication
resource "network" "chat_ui_network" {
  subnet = "10.0.0.0/16"
}

# MongoDB container with persistent storage
resource "container" "mongodb" {
  network {
    id         = resource.network.chat_ui_network.meta.id
    ip_address = "10.0.0.10"
    aliases    = ["mongodb"]
  }

  image {
    name = "mongo:latest"
  }

  port {
    local  = "27017"
    remote = "27017"
    host   = "27017"
  }

  environment = {
    MONGO_INITDB_DATABASE = "chat-ui"
  }

  health_check {
    timeout = "30s"
    tcp {
      address = "localhost:27017"
    }
  }
}

# Hugging Face Chat-UI container
resource "container" "chat_ui" {
  depends_on = ["resource.container.mongodb"]

  network {
    id         = resource.network.chat_ui_network.meta.id
    ip_address = "10.0.0.20"
  }

  image {
    name = "ghcr.io/huggingface/chat-ui:latest"
  }

  port {
    local = "3000"
    host  = "8080"
  }

  # Environment variables configuration
  environment = {
    # MongoDB connection
    MONGODB_URL = "mongodb://mongodb:27017/chat-ui"

    # OpenAI API Configuration
    # Set your OpenAI API key via environment variable or replace the value below
    OPENAI_API_KEY  = env("OPENAI_API_KEY")
    OPENAI_BASE_URL = "http://${docker_ip()}:8000/v1"

    # Application settings
    PUBLIC_ORIGIN          = "http://localhost:8080"
    PUBLIC_APP_NAME        = "Chat UI"
    PUBLIC_APP_DESCRIPTION = "AI Chat Interface powered by Hugging Face"

    # Session and security settings
    COOKIE_NAME = "hf-chat"
    HF_TOKEN    = env("HF_TOKEN")
  }
}

# Output information
output "chat_ui_url" {
  value = "http://localhost:3000"
}

output "mongodb_connection" {
  value = "mongodb://localhost:27017/chat-ui"
}

output "instructions" {
  value = <<-EOF
    Hugging Face Chat-UI Setup Complete!

    1. Ensure your OpenAI API key is set:
       export OPENAI_API_KEY=your_api_key_here

    2. (Optional) Set Hugging Face token for additional features:
       export HF_TOKEN=your_hf_token_here

    3. Access the chat interface at: http://localhost:3000

    4. MongoDB is available at: mongodb://localhost:27017/chat-ui

    Data persistence:
    - MongoDB data is stored in: ./data/mongodb

    To stop the environment:
    - Run: jumppad down
  EOF
}
