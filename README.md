  🏆 Tournament Scheduler

A modern, web-based tournament management system built with Flask that simplifies the process of creating, scheduling, and managing sports tournaments. This application provides an intuitive interface for tournament organizers to generate matches, schedule games with specific venues and durations, and detect scheduling conflicts.

  ✨ Features

  🎯 Tournament Management
-  Create Tournaments: Set up tournaments with custom names, dates, and descriptions
-  Team Management: Add multiple teams and automatically generate round-robin matches
-  Flexible Scheduling: Schedule matches with specific dates, times, venues, and durations (1-10 hours)

  📅 Advanced Scheduling System
-  Duration Control: Set match durations from 1 to 10 hours via dropdown selection
-  Venue Management: Assign specific venues/locations to each match
-  Date Validation: Ensures matches are scheduled within tournament date ranges
-  Conflict Detection: Intelligent conflict detection based on exact matches of date, time, duration, and venue

  🔍 Smart Conflict Detection
-  Precise Conflict Logic: Only flags conflicts when matches have identical date, time, duration, AND venue
-  No False Positives: Different venues or durations won't trigger conflicts even with same date/time
-  Visual Conflict Display: Clear, organized view of all scheduling conflicts with detailed match information

  🎨 Modern User Interface
-  Responsive Design: Beautiful, mobile-friendly interface with modern gradients and animations
-  Intuitive Navigation: Easy-to-use forms and clear visual feedback
-  Real-time Validation: Immediate error checking and user feedback
-  Professional Styling: Clean, modern design with smooth transitions and hover effects

  📖 Match Management
-  View All Matches: Comprehensive match listing with all scheduling details
-  Update Matches: Edit match schedules with full validation
-  Tournament Overview: Browse all tournaments and their associated matches
-  Delete Tournaments: Complete tournament management capabilities

    Technical Stack

-  Backend: Python Flask
-  Database: SQLite with automatic schema migration
-  Frontend: HTML5, CSS3, JavaScript
-  Styling: Custom CSS with modern gradients and animations
-  Icons: Emoji-based icons for intuitive user experience

    Usage Workflow

-   Create Tournament: Set tournament name, start/end dates, and description
-   Generate Matches: Add teams (comma-separated) to automatically create round-robin matches
-   Schedule Matches: Assign date, time, venue, and duration to each match
-   Check Conflicts: Review and resolve any scheduling conflicts
-   Manage Matches: View, update, or modify match schedules as needed

  🎯 Perfect For

-  Sports Tournament Organizers: Manage cricket, football, basketball, or any sport tournaments
-  Event Planners: Schedule events with venue and time constraints
-  League Administrators: Organize multi-team competitions
-  Sports Clubs : Coordinate internal tournaments and matches

 🔧 Key Features Explained

 Conflict Detection Logic
   The system uses a sophisticated four-parameter conflict detection:
-  Date*: Tournament date
-  Time*: Match start time  
-  Duration*: Match length (1-10 hours)
-  Venue*: Match location

   A conflict only occurs when ALL four parameters are identical. This prevents false conflicts when matches have different venues or durations.

  Database Design
-  Automatic Migration: Database schema updates automatically when new features are added
-  Relational Design: Proper foreign key relationships between tournaments and matches
-  Data Integrity: Ensures all required fields are validated before storage

