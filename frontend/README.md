# Riverdale Connect - Frontend

React frontend application for Riverdale Connect pre-handover project governance system.

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **QR Code**: html5-qrcode, react-qr-code
- **Charts**: Recharts
- **PWA**: vite-plugin-pwa

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/
│   │   ├── client.js          # Axios configuration
│   │   ├── auth.js            # Auth API calls
│   │   └── issues.js          # Issues API calls
│   ├── components/
│   │   ├── common/            # Reusable components
│   │   ├── issues/            # Issue-related components
│   │   ├── qrcode/            # QR code components
│   │   └── upload/            # Upload components
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Issues.jsx
│   │   └── Reports.jsx
│   ├── store/
│   │   ├── index.js           # Redux store
│   │   ├── authSlice.js       # Auth state
│   │   └── issuesSlice.js     # Issues state
│   ├── utils/
│   │   ├── constants.js
│   │   ├── validators.js
│   │   └── formatters.js
│   ├── App.jsx                # Main app component
│   ├── main.jsx               # Entry point
│   ├── theme.js               # MUI theme
│   └── index.css              # Global styles
├── package.json
├── vite.config.js
└── .env.example
```

## Setup Instructions

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your API endpoint
```

### Running the Application

**Development mode:**
```bash
npm run dev
# or
yarn dev
```

Visit: http://localhost:5173

**Production build:**
```bash
npm run build
# or
yarn build
```

**Preview production build:**
```bash
npm run preview
# or
yarn preview
```

## Development Guidelines

### Code Style

- Use functional components with hooks
- Follow React best practices
- Use ES6+ features
- Maintain component modularity

### Naming Conventions

- Components: PascalCase (e.g., `IssueCard.jsx`)
- Files: camelCase for utilities, PascalCase for components
- Constants: UPPER_SNAKE_CASE

### Component Structure

```jsx
import React from 'react'
import { Box, Typography } from '@mui/material'

const MyComponent = ({ prop1, prop2 }) => {
  // Hooks
  const [state, setState] = React.useState(null)
  
  // Effects
  React.useEffect(() => {
    // Effect logic
  }, [])
  
  // Handlers
  const handleClick = () => {
    // Handler logic
  }
  
  // Render
  return (
    <Box>
      <Typography>{prop1}</Typography>
    </Box>
  )
}

export default MyComponent
```

### State Management

Use Redux Toolkit for global state:

```javascript
// In slice file
import { createSlice } from '@reduxjs/toolkit'

const mySlice = createSlice({
  name: 'myFeature',
  initialState: {},
  reducers: {
    // Reducers here
  }
})

export const { actions } = mySlice
export default mySlice.reducer
```

### API Calls

Use the centralized API client:

```javascript
import apiClient from '../api/client'

export const getIssues = async () => {
  const response = await apiClient.get('/issues')
  return response.data
}
```

## PWA Features

The application is configured as a Progressive Web App:

- Offline support
- Install prompt
- Service worker caching
- App-like experience on mobile

## Responsive Design

- Mobile-first approach
- Breakpoints: xs, sm, md, lg, xl
- Use MUI Grid and Box for layouts
- Test on multiple devices

## Testing

```bash
npm run test
# or
yarn test
```

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel --prod
```

### Manual Build

```bash
npm run build
# Upload dist/ folder to your hosting
```

## Environment Variables

- `VITE_API_BASE_URL`: Backend API URL
- `VITE_APP_NAME`: Application name
- `VITE_APP_VERSION`: Application version
- `VITE_ENVIRONMENT`: Environment (development/staging/production)

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Performance Optimization

- Code splitting and lazy loading
- Image optimization
- Bundle size monitoring
- Lighthouse score > 90

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.
