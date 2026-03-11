"""
Attendance Analytics Module for ePortal
Provides functions for calculating statistics and generating graphs
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

def load_attendance_data(email):
    """
    Load attendance records for a specific student
    
    Args:
        email: Student email
        
    Returns:
        DataFrame with attendance records
    """
    attendance_file = 'data/attendance.csv'
    
    if not os.path.exists(attendance_file):
        # Return empty DataFrame if no data
        return pd.DataFrame(columns=['email', 'session_id', 'subject', 'timestamp', 'match_score'])
    
    try:
        df = pd.read_csv(attendance_file)
        # Filter by email
        df = df[df['email'] == email].copy()
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Sort by timestamp descending
        df = df.sort_values('timestamp', ascending=False)
        return df
    except Exception as e:
        print(f"Error loading attendance data: {e}")
        return pd.DataFrame(columns=['email', 'session_id', 'subject', 'timestamp', 'match_score'])


def calculate_statistics(df):
    """
    Calculate overall attendance statistics
    
    Args:
        df: Attendance DataFrame
        
    Returns:
        Dictionary with statistics
    """
    total = len(df)
    present = total  # All records are present (we only mark when present)
    
    stats = {
        'total_classes': total,
        'present_count': present,
        'absent_count': 0,  # We don't track absences currently
        'attendance_percentage': 100.0 if total > 0 else 0.0,
        'current_streak': calculate_streak(df)
    }
    
    return stats


def calculate_streak(df):
    """
    Calculate current attendance streak (consecutive days)
    
    Args:
        df: Attendance DataFrame
        
    Returns:
        Number of consecutive days with attendance
    """
    if len(df) == 0:
        return 0
    
    # Get unique dates
    df['date'] = df['timestamp'].dt.date
    unique_dates = sorted(df['date'].unique(), reverse=True)
    
    if len(unique_dates) == 0:
        return 0
    
    # Count consecutive days from today
    streak = 0
    current_date = unique_dates[0]
    
    for date in unique_dates:
        if (current_date - date).days <= 1:
            streak += 1
            current_date = date
        else:
            break
    
    return streak


def calculate_subject_stats(df):
    """
    Calculate per-subject attendance statistics
    
    Args:
        df: Attendance DataFrame
        
    Returns:
        DataFrame with subject statistics
    """
    if len(df) == 0:
        return pd.DataFrame(columns=['subject', 'count', 'percentage'])
    
    # Count attendance per subject
    subject_counts = df['subject'].value_counts().reset_index()
    subject_counts.columns = ['subject', 'count']
    
    # For now, assume each subject has same total classes
    # In production, you'd track total classes per subject
    subject_counts['percentage'] = 100.0  # All marked records are present
    
    return subject_counts


def create_bar_chart(subject_stats):
    """
    Create subject-wise attendance bar chart
    
    Args:
        subject_stats: DataFrame with subject statistics
        
    Returns:
        Plotly figure
    """
    if len(subject_stats) == 0:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No attendance data yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig
    
    # Create bar chart with color coding
    fig = px.bar(
        subject_stats,
        x='subject',
        y='count',
        title='📊 Subject-wise Attendance',
        labels={'count': 'Classes Attended', 'subject': 'Subject'},
        color='count',
        color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
        text='count'
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig


def create_pie_chart(stats):
    """
    Create overall attendance pie chart
    
    Args:
        stats: Statistics dictionary
        
    Returns:
        Plotly figure
    """
    if stats['total_classes'] == 0:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No attendance data yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig
    
    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=['Present', 'Absent'],
        values=[stats['present_count'], stats['absent_count']],
        marker=dict(colors=['#10B981', '#EF4444']),
        hole=0.4,
        textinfo='label+percent',
        textfont=dict(size=16)
    )])
    
    fig.update_layout(
        title='🥧 Overall Attendance Distribution',
        height=400,
        showlegend=True
    )
    
    return fig


def create_line_chart(df):
    """
    Create attendance trend line chart
    
    Args:
        df: Attendance DataFrame
        
    Returns:
        Plotly figure
    """
    if len(df) == 0:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No attendance data yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig
    
    # Group by date and count
    df['date'] = df['timestamp'].dt.date
    daily_counts = df.groupby('date').size().reset_index(name='count')
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
    
    # Create line chart
    fig = px.line(
        daily_counts,
        x='date',
        y='count',
        title='📈 Attendance Trend (Last 30 Days)',
        labels={'count': 'Classes Attended', 'date': 'Date'},
        markers=True
    )
    
    fig.update_traces(
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=8, color='#10B981')
    )
    
    fig.update_layout(
        height=400,
        hovermode='x unified'
    )
    
    return fig


def format_attendance_table(df):
    """
    Format attendance DataFrame for display
    
    Args:
        df: Attendance DataFrame
        
    Returns:
        Formatted DataFrame
    """
    if len(df) == 0:
        return df
    
    # Select and rename columns
    display_df = df[['subject', 'timestamp', 'match_score']].copy()
    display_df.columns = ['Subject', 'Date & Time', 'Match Score']
    
    # Format timestamp
    display_df['Date & Time'] = display_df['Date & Time'].dt.strftime('%Y-%m-%d %I:%M %p')
    
    # Format match score as percentage
    display_df['Match Score'] = display_df['Match Score'].apply(lambda x: f"{x:.1%}")
    
    # Add status column (all present)
    display_df.insert(2, 'Status', '✅ Present')
    
    return display_df
