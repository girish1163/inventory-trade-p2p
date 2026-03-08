# Vercel Deployment Guide

This guide will help you deploy your Inventory Management System to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: For version control and deployment
3. **Node.js**: Installed on your local machine

## Project Structure for Vercel

```
windsurf-project/
├── api/                    # Serverless functions (Flask API)
│   ├── index.py           # Main Flask application
│   └── requirements.txt   # Python dependencies
├── client/                 # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── vercel.json            # Vercel configuration
└── README.md
```

## Deployment Steps

### 1. Prepare Your Project

The project is already configured for Vercel deployment with:
- `vercel.json` configuration file
- `api/index.py` serverless function
- Updated API endpoints to use relative paths
- Removed proxy configuration from package.json

### 2. Push to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Vercel deployment"

# Create GitHub repository and push
git branch -M main
git remote add origin https://github.com/yourusername/inventory-management.git
git push -u origin main
```

### 3. Deploy to Vercel

#### Option A: Using Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy from project root:
```bash
cd windsurf-project
vercel
```

4. Follow the prompts:
- Set up and deploy project
- Link to existing Vercel project or create new one
- Confirm settings

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Vercel will auto-detect the framework (Flask + React)
5. Click "Deploy"

### 4. Environment Variables (Optional)

If you need environment variables, add them in Vercel Dashboard:
- Go to Project Settings → Environment Variables
- Add any required variables (currently using in-memory database, so none needed)

## Features After Deployment

✅ **Live URL**: Your app will be available at `https://your-project-name.vercel.app`

✅ **Four Sectors Available**:
- 📋 Stock List
- 📦 Inventory Management  
- 💰 Billing
- 📝 Notes

✅ **Indian Rupee Currency**: All amounts displayed in ₹

✅ **Zero Initial Data**: Fresh start with empty inventory, bills, and notes

✅ **Authentication**: Login with User ID: 743663, Password: girish7890@A

## Testing Your Deployment

1. **Visit your Vercel URL**
2. **Login with credentials**:
   - User ID: 743663
   - Password: girish7890@A
3. **Test all features**:
   - Add inventory items
   - Create invoices
   - Add notes
   - Check dashboard statistics

## Automatic Deployments

Vercel will automatically redeploy your app when you:
- Push changes to the main branch
- Create pull requests
- Merge pull requests

## Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check `vercel.json` syntax
   - Ensure `api/requirements.txt` is correct
   - Verify all API paths are relative

2. **API Calls Fail**:
   - Ensure all API endpoints use `/api/` prefix
   - Check CORS settings in `api/index.py`

3. **404 Errors**:
   - Verify `vercel.json` routing configuration
   - Check file structure matches expected layout

### Debug Mode

Add debug logging by setting environment variable in Vercel:
- `DEBUG=true`

## Performance Optimization

Your deployment includes:
- ✅ Serverless functions for API
- ✅ Static asset optimization
- ✅ Global CDN distribution
- ✅ Automatic HTTPS
- ✅ Custom domain support

## Next Steps

1. **Add Custom Domain**: In Vercel Dashboard → Domains
2. **Set Up Analytics**: Vercel Analytics for performance monitoring
3. **Environment Variables**: Add database connection for persistent storage
4. **Custom Branding**: Update colors, logos, and styling

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Flask on Vercel**: [vercel.com/guides/flask](https://vercel.com/guides/flask)
- **React on Vercel**: [vercel.com/guides/react](https://vercel.com/guides/react)

---

**🎉 Congratulations! Your Inventory Management System is now ready for Vercel deployment!**
