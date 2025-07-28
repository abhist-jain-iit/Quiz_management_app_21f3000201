# Quiz Master V2 - Frontend

A modern Vue.js frontend application for the Quiz Master V2 project, built for the MAD II course.

## Features

- **Vue.js 3** with Composition API
- **Bootstrap 5** for responsive design
- **Chart.js** for analytics and data visualization
- **Vue Router** for navigation
- **Axios** for API communication
- **JWT Authentication** with automatic token management
- **Responsive Design** for mobile and desktop
- **Real-time Quiz Timer** with auto-submission
- **Admin Dashboard** with complete CRUD operations
- **User Dashboard** with quiz attempts and progress tracking

## Technology Stack

- Vue.js 3
- Vue Router 4
- Bootstrap 5
- Chart.js 4
- Axios
- Vite (Build tool)

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Running backend server (Flask API)

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:8080`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/          # Reusable Vue components
│   ├── views/              # Page components
│   │   ├── auth/           # Authentication pages
│   │   └── admin/          # Admin management pages
│   ├── services/           # API service layer
│   ├── router/             # Vue Router configuration
│   ├── App.vue             # Root component
│   └── main.js             # Application entry point
├── index.html              # HTML template
├── vite.config.js          # Vite configuration
└── package.json            # Dependencies and scripts
```

## Key Features

### Authentication
- User registration and login
- JWT token management
- Role-based access control (Admin/User)
- Automatic token refresh

### User Features
- Dashboard with quiz statistics
- Browse available quizzes by subject/chapter
- Take timed quizzes with real-time countdown
- View quiz results and performance analytics
- Export quiz history to CSV
- Profile management

### Admin Features
- Comprehensive admin dashboard
- Subject management (CRUD)
- Chapter management (CRUD)
- Quiz management (CRUD)
- Question management (CRUD)
- User management
- Search functionality
- Export user data to CSV
- Analytics and reporting

### Quiz Taking Experience
- Real-time timer with auto-submission
- Question navigation sidebar
- Progress tracking
- Prevent accidental page refresh during quiz
- Immediate results after submission

## API Integration

The frontend communicates with the Flask backend API running on `http://localhost:5000`. All API calls are handled through the `services/api.js` file with automatic JWT token management.

### Key API Endpoints Used:
- `/api/auth/*` - Authentication
- `/api/subjects/*` - Subject management
- `/api/chapters/*` - Chapter management
- `/api/quizzes/*` - Quiz management
- `/api/questions/*` - Question management
- `/api/scores/*` - Score management
- `/api/dashboard` - Dashboard data
- `/api/users/*` - User management (Admin)
- `/api/search` - Search functionality
- `/api/export/*` - Data export

## Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

Bootstrap 5 classes are used throughout for responsive layouts, and custom CSS ensures optimal viewing on all devices.

## Charts and Analytics

Chart.js is integrated for data visualization:
- Performance trend charts
- Subject-wise performance breakdown
- User registration trends (Admin)
- Quiz performance overview (Admin)

## Development

### Code Style
- Vue.js Composition API
- ES6+ JavaScript
- Bootstrap utility classes
- Semantic HTML structure

### State Management
- Local component state using Vue 3 reactivity
- JWT tokens stored in localStorage
- API responses cached where appropriate

## Deployment

1. Build the application:
```bash
npm run build
```

2. Serve the `dist` directory using any static file server
3. Ensure the backend API is accessible from the deployment environment
4. Update API base URL in `src/services/api.js` if needed

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow Vue.js best practices
2. Use Bootstrap classes for styling
3. Ensure responsive design
4. Add proper error handling
5. Test on multiple devices

## Demo Credentials

- **Admin**: username: `admin`, password: `Admin@123`
- **User**: Register a new account through the registration form

## Notes

- The application requires the backend Flask API to be running
- All forms include client-side validation
- Error messages are displayed for failed API calls
- Loading states are shown during API requests
- The quiz timer automatically submits when time expires
