import streamlit as st
from datetime import datetime
import uuid

st.set_page_config(page_title="Projects - Emoticon", layout="wide")

# Initialize theme state based on time of day
if 'dark_mode' not in st.session_state:
    from datetime import datetime
    current_hour = datetime.now().hour
    # Default to light mode during daytime (6 AM - 6 PM)
    st.session_state.dark_mode = not (6 <= current_hour < 18)

# Initialize projects data
if 'projects' not in st.session_state:
    st.session_state.projects = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Emoticon AI Roadmap',
            'type': 'startup',
            'description': 'Strategic roadmap for AI emotion detection platform',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'AI Screen Automation Comp...',
            'type': 'startup',
            'description': 'Automated screen recording and analysis system',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'AI Website Builders for Start...',
            'type': 'startup',
            'description': 'Automated website generation for startups',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Emoticon AI Learning Road...',
            'type': 'startup',
            'description': 'Educational platform for AI emotion detection',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'ELEC3117',
            'type': 'course',
            'description': 'Electronics and Signal Processing',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'CS',
            'type': 'course',
            'description': 'Computer Science Fundamentals',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Industrial Training',
            'type': 'course',
            'description': 'Professional development and training',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        }
    ]

# Apply theme
if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .sidebar-item {
        background-color: #2d2d2d;
        color: #ffffff;
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .sidebar-item:hover {
        background-color: #404040;
    }
    .sidebar-item.active {
        background-color: #0066cc;
        color: #ffffff;
    }
    .project-card {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    .project-card:hover {
        border-color: #0066cc;
    }
    .project-type {
        background-color: #404040;
        color: #cccccc;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        display: inline-block;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .sidebar-item {
        background-color: #f8f9fa;
        color: #000000;
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #e9ecef;
    }
    .sidebar-item:hover {
        background-color: #e9ecef;
    }
    .sidebar-item.active {
        background-color: #0066cc;
        color: #ffffff;
    }
    .project-card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    .project-card:hover {
        border-color: #0066cc;
    }
    .project-type {
        background-color: #f8f9fa;
        color: #6c757d;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        display: inline-block;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Navigation")
    
    # Sidebar menu items
    menu_items = [
        ("New chat", "💬"),
        ("Search chats", "🔍"),
        ("Library", "📚"),
        ("Codex", "⏰"),
        ("Sora", "▶️"),
        ("GPTs", "🤖"),
        ("New project", "📁"),
        ("Startup", "🚀"),
        ("View plans", "⭐")
    ]
    
    for item, icon in menu_items:
        if st.button(f"{icon} {item}", key=f"nav_{item}", use_container_width=True):
            if item == "New project":
                st.session_state.show_new_project = True
            elif item == "Startup":
                st.session_state.filter_type = "startup"
            elif item == "New chat":
                st.success(f"Opening {item}...")
            else:
                st.info(f"Selected: {item}")

with col2:
    st.markdown("### Projects Dashboard")
    
    # Project type filter
    filter_type = st.selectbox(
        "Filter by type:",
        ["All", "startup", "course", "other"],
        key="project_filter"
    )
    
    # New project form
    if st.session_state.get('show_new_project', False):
        st.markdown("#### Create New Project")
        
        with st.form("new_project_form"):
            project_name = st.text_input("Project Name")
            project_type = st.selectbox("Project Type", ["startup", "course", "other"])
            project_description = st.text_area("Description")
            
            submitted = st.form_submit_button("Create Project")
            
            if submitted and project_name:
                new_project = {
                    'id': str(uuid.uuid4()),
                    'name': project_name,
                    'type': project_type,
                    'description': project_description,
                    'created': datetime.now().strftime('%Y-%m-%d'),
                    'status': 'active'
                }
                st.session_state.projects.append(new_project)
                st.session_state.show_new_project = False
                st.success(f"Created project: {project_name}")
                st.rerun()
    
    # Filter projects
    filtered_projects = st.session_state.projects
    if filter_type != "All":
        filtered_projects = [p for p in st.session_state.projects if p['type'] == filter_type]
    
    # Display projects
    st.markdown("#### Your Projects")
    
    if filtered_projects:
        for project in filtered_projects:
            st.markdown(f"""
            <div class="project-card">
                <div class="project-type">{project['type'].upper()}</div>
                <h4>{project['name']}</h4>
                <p>{project['description']}</p>
                <small>Created: {project['created']} | Status: {project['status']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons for each project
            proj_col1, proj_col2, proj_col3 = st.columns(3)
            with proj_col1:
                if st.button("Open", key=f"open_{project['id']}"):
                    st.info(f"Opening {project['name']}...")
            with proj_col2:
                if st.button("Edit", key=f"edit_{project['id']}"):
                    st.info(f"Editing {project['name']}...")
            with proj_col3:
                if st.button("Delete", key=f"delete_{project['id']}"):
                    st.session_state.projects = [p for p in st.session_state.projects if p['id'] != project['id']]
                    st.success(f"Deleted {project['name']}")
                    st.rerun()
    else:
        st.info("No projects found. Create your first project!")

# Navigation buttons
st.markdown("---")
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

with nav_col1:
    if st.button("Home", key="nav_home", use_container_width=True):
        st.switch_page("app.py")

with nav_col2:
    if st.button("About", key="nav_about", use_container_width=True):
        st.switch_page("pages/about.py")

with nav_col3:
    if st.button("Contact", key="nav_contact", use_container_width=True):
        st.switch_page("pages/contact.py")

with nav_col4:
    if st.button("Career", key="nav_career", use_container_width=True):
        st.switch_page("pages/career.py")

with nav_col5:
    if st.button("Projects", key="nav_projects", use_container_width=True):
        st.rerun()