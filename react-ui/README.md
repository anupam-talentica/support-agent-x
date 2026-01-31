# Support Agent X

A collaborative multi-agent support platform with intelligent chat assistance, ticket management, and admin dashboard—powered by the Support Agent X agent system.

## 🚀 Live Demo

**URL**: https://lovable.dev/projects/1a5550f9-912b-410d-9e05-1668fa8ca516

## 📋 Features & Functionalities

### 🤖 **AI-Powered Chat Assistant**
- **ChatGPT 4.0 Integration**: Intelligent responses for all electric scooter queries
- **Web Search Capability**: Automatic detection and handling of time-sensitive queries
- **Conversation Memory**: Context-aware responses with conversation history
- **Multi-Brand Support**: Expert knowledge for OLA, Ather, TVS, Bajaj, and other scooter brands
- **Smart Fallback System**: Local knowledge base when AI is unavailable

### 🎫 **Support Ticket Management**
- **Direct Ticket Creation**: Create tickets via dedicated button in chat interface
- **Message-Based Tickets**: Convert chat messages to support tickets
- **Category & Priority System**: Organize tickets by type and urgency
- **Status Tracking**: Monitor ticket progress through different states
- **User Assignment**: Link tickets to specific users

### 👤 **User Management**
- **Phone-Based Authentication**: Login using phone numbers
- **User Profiles**: Manage user information and preferences
- **Role-Based Access**: Different permissions for users and admins
- **Session Management**: Secure user sessions with logout functionality

### 🛠️ **Admin Dashboard**
- **Ticket Overview**: View and manage all support tickets
- **User Management**: Admin access to user accounts
- **Query Analytics**: Track unresolved queries and feedback
- **System Monitoring**: Monitor AI usage and system performance

### 📁 **File Management**
- **File Upload**: Attach images, PDFs, and documents to chat
- **File Preview**: Display file information and metadata
- **Multi-Format Support**: Support for various file types

### 🔧 **Additional Features**
- **Rating System**: Like/dislike responses for quality feedback
- **Feedback Collection**: Capture user feedback for improvement
- **Real-Time Updates**: Live chat interface with typing indicators
- **Responsive Design**: Works on desktop and mobile devices
- **Dark/Light Mode**: Automatic theme support

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn package manager

### Installation

```sh
# Clone the repository
git clone https://github.com/your-org/support-agent-x.git

# Navigate to project directory
cd support-agent-x/react-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

## 🔐 Admin Access

### Admin Login Credentials
You can login as an admin using any of these phone numbers:
- **7777777777** (all 7s)
- **8888888888** (all 8s)  
- **9999999999** (all 9s)

### Admin Features
- Access to Admin Dashboard
- View all support tickets
- Manage user accounts
- Monitor system analytics
- View unresolved queries

## ⚙️ Feature Configuration

### 🤖 Enable ChatGPT 4.0 (Recommended)

1. **Get OpenAI API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an account and generate an API key
   - Copy the key (starts with `sk-`)

2. **Configure in App**:
   - Click the **Settings** icon in the chat header
   - Find the "ChatGPT 4.0 (Primary Assistant)" section
   - Enter your OpenAI API key
   - Click "Enable ChatGPT 4.0"

3. **Benefits**:
   - Intelligent responses for ALL queries
   - Automatic web search for time-sensitive information
   - Conversation memory and context awareness
   - Enhanced troubleshooting capabilities

### 📊 Usage Tracking
- Query count is displayed in the chat header
- Estimated costs are shown in settings
- Usage statistics are stored locally

## 🏗️ Architecture

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Lucide React** for icons

### Services
- **OpenAI Service**: ChatGPT 4.0 integration with web search
- **Ticket Service**: Support ticket management
- **User Service**: Authentication and user management
- **Perplexity Service**: Alternative web search (optional)

### Storage
- **LocalStorage**: User sessions, chat history, tickets
- **Browser Storage**: Cached responses and settings

## 📱 User Interface

### Chat Interface
- Clean, modern design with message bubbles
- File attachment support
- Real-time typing indicators
- Message rating and feedback system
- Direct ticket creation button

### Dashboard
- Ticket overview with filters
- User management interface
- Analytics and reporting
- Settings configuration

## 🔧 Development

### Available Scripts

```sh
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Project Structure

```
src/
├── components/          # Reusable UI components
│   └── ui/             # shadcn/ui components
├── pages/              # Main application pages
│   ├── Chat.tsx        # Chat interface
│   ├── Dashboard.tsx   # Admin dashboard
│   ├── Login.tsx       # Authentication
│   └── ...
├── services/           # API and business logic
│   ├── openai.ts       # ChatGPT integration
│   ├── ticketService.ts # Ticket management
│   └── userService.ts  # User management
├── types/              # TypeScript type definitions
├── hooks/              # Custom React hooks
└── lib/                # Utility functions
```

## 🎯 Usage Guide

### For Regular Users

1. **Login**: Use your phone number to authenticate
2. **Chat**: Ask questions about electric scooters
3. **Get Help**: Use the help desk ticket button for support
4. **Track Issues**: Monitor ticket progress in dashboard

### For Admins

1. **Login**: Use admin credentials (7777777777, 8888888888, or 9999999999)
2. **Dashboard**: Access admin dashboard for ticket management
3. **Monitor**: View system analytics and user feedback
4. **Manage**: Handle support tickets and user accounts

## 🛡️ Security Features

- **Phone-based Authentication**: Secure login system
- **Session Management**: Automatic session handling
- **API Key Protection**: Secure storage of API keys
- **Role-based Access**: Different permissions for users and admins

## 🔄 Updates & Maintenance

### Recent Updates
- ChatGPT 4.0 integration with conversation memory
- Enhanced web search capabilities
- Direct help desk ticket creation
- Improved admin dashboard
- Better error handling and fallbacks

### Future Enhancements
- Real-time notifications
- Advanced analytics dashboard
- Multi-language support
- Mobile app version

## 🐛 Troubleshooting

### Common Issues

1. **ChatGPT not responding**:
   - Check OpenAI API key in settings
   - Verify API key has sufficient credits
   - Check internet connection

2. **Login issues**:
   - Ensure phone number is 10 digits
   - Try admin numbers: 7777777777, 8888888888, 9999999999
   - Clear browser cache if needed

3. **Tickets not creating**:
   - Check if user is logged in
   - Verify all required fields are filled
   - Try refreshing the page

## 📞 Support

For technical issues or questions:
- Create a ticket using the help desk button
- Contact admin users
- Check console logs for error details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- **Live Demo**: https://lovable.dev/projects/1a5550f9-912b-410d-9e05-1668fa8ca516
- **OpenAI Platform**: https://platform.openai.com/
- **Repository**: https://github.com/your-org/support-agent-x

---

**Built with ❤️ for electric scooter enthusiasts**
