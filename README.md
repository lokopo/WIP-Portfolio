# Job Application Tracker

A comprehensive dashboard to track your job applications, manage resumes, cover letters, and other documentation. Built with React, Vite, and Tailwind CSS.

## Features

### 📊 Dashboard
- Overview statistics (total applications, status breakdown)
- Recent job applications
- Document management summary
- Quick access to key actions

### 💼 Job Applications
- **Add new applications** with comprehensive details:
  - Company and position information
  - Location and salary details
  - Contact information
  - Job descriptions
  - Application URLs
  - Custom notes and reminders
- **Track application status**: Applied, Interviewing, Offered, Rejected, Withdrawn
- **Search and filter** applications by company, position, location, or status
- **Sort** by date, company, or status
- **Edit and update** application details
- **Delete** applications with confirmation

### � Document Management
- **Organize documents** by type:
  - Resumes
  - Cover Letters
  - Portfolios
  - Certificates
  - Other documents
- **Add document metadata**:
  - Name and description
  - File URLs or paths
  - Tags for easy categorization
- **Search and filter** documents
- **Edit and delete** document information

### 🎨 Modern UI
- Clean, responsive design
- Dark/light theme support
- Intuitive navigation
- Mobile-friendly interface
- Beautiful icons and visual feedback

### 💾 Data Persistence
- Local storage for data persistence
- No external dependencies or setup required
- Automatic data backup and recovery

## Getting Started

### Prerequisites
- Node.js (version 16 or higher)
- npm or yarn package manager

### Installation

1. **Clone or download** the project files

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser** and navigate to `http://localhost:3000`

### Building for Production

To create a production build:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage Guide

### Adding Your First Job Application

1. Click "Add Job" from the sidebar or dashboard
2. Fill in the required information:
   - **Company Name** and **Position Title** (required)
   - **Location**, **Salary**, and **Status**
   - **Contact information** (optional)
   - **Job description** (paste the full description)
   - **Application URL** (link to the job posting)
   - **Documents used** (which resume/cover letter you used)
   - **Notes** (any additional information)

3. Click "Save Application"

### Managing Documents

1. Navigate to the "Documents" section
2. Click "Add Document" to create a new document entry
3. Fill in:
   - **Document Name** (e.g., "Software Engineer Resume v2")
   - **Document Type** (Resume, Cover Letter, etc.)
   - **Description** (optional)
   - **File URL or Path** (where the file is stored)
   - **Tags** (comma-separated for easy searching)

### Tracking Application Progress

1. View all applications in the "Job Applications" section
2. Use filters to find specific applications
3. Click on any application to view/edit details
4. Update the status as your application progresses
5. Add notes about interviews, follow-ups, or decisions

## Data Structure

### Job Application Fields
- `id`: Unique identifier
- `company`: Company name
- `position`: Job title
- `location`: Job location
- `salary`: Salary range
- `status`: Application status
- `appliedDate`: Date applied
- `jobDescription`: Full job description
- `applicationUrl`: Link to application
- `contactPerson`: Hiring manager name
- `contactEmail`: Contact email
- `contactPhone`: Contact phone
- `notes`: Additional notes
- `resumeUsed`: Resume version used
- `coverLetterUsed`: Cover letter version used
- `createdAt`: Creation timestamp
- `updatedAt`: Last update timestamp

### Document Fields
- `id`: Unique identifier
- `name`: Document name
- `type`: Document type (resume, cover-letter, etc.)
- `description`: Document description
- `fileUrl`: File path or URL
- `tags`: Array of tags
- `createdAt`: Creation timestamp
- `updatedAt`: Last update timestamp

## Customization

### Styling
The application uses Tailwind CSS for styling. You can customize the appearance by modifying:
- `src/index.css` for global styles
- `tailwind.config.js` for theme configuration
- Individual component files for specific styling

### Adding Features
The modular structure makes it easy to add new features:
- Add new pages in `src/pages/`
- Create new components in `src/components/`
- Extend the context in `src/contexts/JobContext.jsx`

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Data Backup

Your data is stored locally in your browser's localStorage. To backup your data:

1. Open browser developer tools (F12)
2. Go to Application/Storage tab
3. Find "Local Storage" → "http://localhost:3000"
4. Copy the values for `jobApplications` and `jobDocuments`

To restore data, paste the values back into the same localStorage keys.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source and available under the MIT License.

---

**Happy job hunting! 🚀** 