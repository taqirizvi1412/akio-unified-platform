# Setup Guide

## Prerequisites
- Node.js 14+ installed
- HubSpot account (free tier is fine)
- Basic understanding of REST APIs

## Installation Steps

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your HubSpot API key to the `.env` file

3. **Get HubSpot API Key**
   - Log in to HubSpot
   - Go to Settings â†’ Integrations â†’ Private Apps
   - Create a new private app
   - Set required scopes (contacts read/write, calls read/write)
   - Copy the access token

4. **Start the server**
   ```bash
   npm start
   ```

5. **Access the application**
   - Open http://localhost:3000 in your browser
   - The frontend interface will load automatically

## Testing
Run tests with:
```bash
npm test
```

## Development Mode
For auto-restart on file changes:
```bash
npm run dev
```

## Troubleshooting
- Ensure all dependencies are installed
- Check that your API key is valid
- Verify Node.js version is 14+
- Check console for error messages
