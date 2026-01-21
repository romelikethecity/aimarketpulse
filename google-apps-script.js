/**
 * AI Market Pulse - Google Apps Script for Form Submissions
 * 
 * SETUP INSTRUCTIONS:
 * 
 * 1. Open your Google Sheet (the one with your registrants)
 * 
 * 2. Go to Extensions → Apps Script
 * 
 * 3. Delete any existing code and paste this entire file
 * 
 * 4. Update the SHEET_NAME below if your sheet tab isn't named "Registrants"
 * 
 * 5. Click the disk icon to save (or Ctrl+S)
 * 
 * 6. Click "Deploy" → "New deployment"
 *    - Click the gear icon next to "Select type" → choose "Web app"
 *    - Description: "AI Market Pulse Form Handler"
 *    - Execute as: "Me"
 *    - Who has access: "Anyone"
 *    - Click "Deploy"
 * 
 * 7. Click "Authorize access" and grant permissions
 *    - Choose your Google account
 *    - Click "Advanced" → "Go to AI Market Pulse Form Handler (unsafe)"
 *    - Click "Allow"
 * 
 * 8. Copy the Web app URL (looks like: https://script.google.com/macros/s/xxx/exec)
 * 
 * 9. Paste that URL into your website's join/index.html where it says:
 *    const GOOGLE_SCRIPT_URL = 'YOUR_GOOGLE_APPS_SCRIPT_URL_HERE';
 * 
 * That's it! Form submissions will now append to your Google Sheet.
 */

// ============================================
// CONFIGURATION - Update this if needed
// ============================================

const SHEET_NAME = 'Registrants';  // Name of the sheet tab (check your spreadsheet)

// Column order in your sheet (must match your existing columns)
const COLUMNS = [
  'First Name',
  'Last Name', 
  'Business Email',
  'LinkedIn URL',
  'Company',
  'Job Title',
  'Date Joined'
];

// ============================================
// DO NOT EDIT BELOW THIS LINE
// ============================================

/**
 * Handle POST requests from the website form
 */
function doPost(e) {
  try {
    // Parse the incoming JSON data
    const data = JSON.parse(e.postData.contents);
    
    // Get the spreadsheet and sheet
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAME);
    
    if (!sheet) {
      throw new Error(`Sheet "${SHEET_NAME}" not found. Check the SHEET_NAME configuration.`);
    }
    
    // Build the row data in the correct column order
    const rowData = [
      data.first_name || '',
      data.last_name || '',
      data.email || '',
      data.linkedin_url || '',
      data.company || '',
      data.job_title || '',
      data.date_joined || new Date().toLocaleDateString('en-US')
    ];
    
    // Append the row to the sheet
    sheet.appendRow(rowData);
    
    // Return success response
    return ContentService
      .createTextOutput(JSON.stringify({ 
        status: 'success', 
        message: 'Registration saved successfully' 
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    // Log the error for debugging
    console.error('Error processing form submission:', error);
    
    // Return error response
    return ContentService
      .createTextOutput(JSON.stringify({ 
        status: 'error', 
        message: error.toString() 
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Handle GET requests (for testing)
 */
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ 
      status: 'ok', 
      message: 'AI Market Pulse Form Handler is running. Use POST to submit data.' 
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Test function - run this to verify setup
 * Go to Run → testSubmission to test
 */
function testSubmission() {
  const testData = {
    postData: {
      contents: JSON.stringify({
        first_name: 'Test',
        last_name: 'User',
        email: 'test@example.com',
        linkedin_url: 'https://linkedin.com/in/testuser',
        company: 'Test Company',
        job_title: 'Test Engineer',
        date_joined: new Date().toLocaleDateString('en-US')
      })
    }
  };
  
  const result = doPost(testData);
  console.log(result.getContent());
}
