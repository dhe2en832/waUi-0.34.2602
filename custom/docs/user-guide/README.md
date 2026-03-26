# WACSA-MD2 UI - Version 2.0

Modern WhatsApp-like desktop client for WACSA-MD2 server with login-first authentication flow.

## ✨ Features

### 🔐 Secure Login
- Login-first flow - no access without authentication
- Remember me functionality
- Secure credential storage
- Auto-login for returning users

### 💬 WhatsApp-Like Interface
- **Chat List**: Contact list with avatars, last message preview, unread badges
- **Chat View**: WhatsApp-style message bubbles
  - Received messages: Left-aligned, gray bubbles
  - Sent messages: Right-aligned, blue bubbles
  - Timestamps and delivery status (✓✓)
  - Media indicators
- **Search**: Quick contact search
- **Date Separators**: Messages grouped by date (Today, Yesterday, etc.)

### 📱 Modern UI/UX
- Clean, intuitive interface
- Responsive layout
- Smooth navigation
- Real-time message updates
- Status indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- WACSA-MD2 server running
- Network access to server

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the application**:
```bash
python main_new.py
```

3. **Login**:
   - Enter server URL (e.g., `http://192.168.100.13:8008`)
   - Enter email: `wa@csacomputer.com`
   - Enter password: `csa2025`
   - Click "Login"

## 📁 Project Structure

```
wacsa-md2-ui/
├── src/
│   ├── ui/
│   │   ├── login_window.py      # Login dialog
│   │   ├── main_window.py       # Main app window
│   │   └── components/
│   │       ├── chat_list.py     # Contact list
│   │       ├── chat_view.py     # Conversation view
│   │       └── message_bubble.py # Message components
│   ├── api/
│   │   └── client.py            # API client
│   ├── utils/
│   │   └── ...                  # Utility functions
│   └── models/
│       └── ...                  # Data models
├── assets/
│   ├── icons/                   # App icons
│   └── images/                  # UI images
├── config/
│   └── credentials.json         # Saved credentials (auto-generated)
├── main_new.py                  # Application entry point
└── requirements.txt             # Python dependencies
```

## 🎨 UI Components

### Login Window
- Centered modal dialog
- Server URL configuration
- Email/password authentication
- Remember me option
- Error handling with user-friendly messages

### Main Window

#### Sidebar
- User profile with avatar
- Navigation menu (Dashboard, Messages, Settings)
- Logout button

#### Messages Page
- **Left Panel**: Chat list with search
  - Contact avatars (first letter)
  - Contact name
  - Last message preview
  - Timestamp
  - Unread count badge
  
- **Right Panel**: Chat conversation
  - Contact header with status
  - Scrollable message area
  - Message bubbles (sent/received)
  - Message input with send button
  - Media attach button

#### Dashboard
- Statistics cards
- Message counts
- Active chats overview

#### Settings
- Server configuration
- Connection status
- Refresh messages button

## 🔧 Configuration

### Server URL
Default: `http://192.168.100.13:8008`

### Credentials
Stored in: `config/credentials.json` (auto-generated)

**Note**: In production, credentials should be encrypted!

## 📡 API Integration

### Endpoints Used
- `POST /auth/login` - User authentication
- `GET /log/received-message` - Get received messages
- `GET /log/sent-message` - Get sent messages
- `POST /message/send-text` - Send text message
- `POST /message/send-media` - Send media message

### Authentication
- Token-based authentication
- Token stored in session
- Auto-refresh on reconnect

## 🎯 Usage

### Sending Messages
1. Select contact from chat list
2. Type message in input box
3. Press Enter or click Send button

### Viewing Messages
- Messages auto-load when selecting contact
- Scroll to view message history
- Messages grouped by date

### Refreshing Messages
- Go to Settings page
- Click "Refresh Messages" button
- Or restart application

## 🔨 Building Executable

```bash
python -m PyInstaller --name "WACSA-MD2-UI" --windowed --onefile --hidden-import=requests --hidden-import=customtkinter --hidden-import=loguru main_new.py
```

Output: `dist/WACSA-MD2-UI.exe`

## 🐛 Troubleshooting

### Login Issues
- **Cannot connect to server**: Check server URL and ensure WACSA-MD2 is running
- **Invalid credentials**: Verify email and password
- **Token error**: Clear `config/credentials.json` and login again

### Message Issues
- **Messages not loading**: Click "Refresh Messages" in Settings
- **Cannot send message**: Check server connection and authentication

### UI Issues
- **Window not appearing**: Check if process is running, restart application
- **Blank screen**: Check console for errors, verify Python version

## 📝 Development

### Running in Development Mode
```bash
python main_new.py
```

### Code Structure
- **UI Components**: Modular, reusable components in `src/ui/components/`
- **Pages**: Separate page files in `src/ui/pages/`
- **API Client**: Centralized API communication in `src/api/client.py`
- **Models**: Data models in `src/models/`

### Adding New Features
1. Create component in `src/ui/components/`
2. Import in parent window/page
3. Integrate with API client
4. Test thoroughly

## 🔄 Migration from Old Version

The old `main.py` is preserved. To use the new version:

1. Run `main_new.py` instead of `main.py`
2. Login with credentials
3. All features are available in new UI

## 📄 License

Copyright © 2026 WACSA Team

## 🤝 Support

For issues or questions, please contact the development team.

---

**Version**: 2.0.0  
**Last Updated**: March 26, 2026  
**Author**: WACSA Development Team
