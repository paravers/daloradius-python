"""
daloRADIUS Graph Module Data Models

This module contains Pydantic models for all data structures used in the Graph functionality.
These models represent the data structures from the PHP files in app/operators/graphs-*.php files.

Models follow SOLID principles:
- SRP: Each model has a single responsibility 
- OCP: Models are extensible through inheritance
- DIP: Models depend on abstractions (base classes)
- ISP: Interfaces are segregated by functionality
- LSP: Derived models can replace base models
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from ipaddress import IPv4Address


class BaseGraphModel(BaseModel):
    """Base model for all graph-related data structures"""
    
    class Config:
        # Enable ORM mode for database integration
        orm_mode = True
        # Use enum values instead of enum names
        use_enum_values = True
        # Allow population by field name or alias
        allow_population_by_field_name = True
        # Validate assignments
        validate_assignment = True


class GraphType(str, Enum):
    """Graph time period types - follows ISP principle"""
    DAILY = "daily"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class DataSize(str, Enum):
    """Data size units for traffic graphs - follows OCP principle for extension"""
    MEGABYTES = "megabytes"
    GIGABYTES = "gigabytes"


class GraphCategory(str, Enum):
    """Graph data categories - follows OCP principle"""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    LOGIN = "login"


class ChartType(str, Enum):
    """Chart display types - follows ISP principle"""
    DAILY = "Daily"
    MONTHLY = "Monthly"
    GRAPHS = "Graphs"
    STATISTICS = "Statistics"


# Base models for different graph types - follows SRP principle

class BaseGraphQuery(BaseGraphModel):
    """Base model for graph query parameters"""
    type: GraphType = Field(default=GraphType.DAILY, description="Time period type for the graph")
    goto_stats: bool = Field(default=False, description="Whether to redirect to statistics tab")


class BaseTrafficQuery(BaseGraphQuery):
    """Base model for traffic-related graph queries"""
    size: DataSize = Field(default=DataSize.MEGABYTES, description="Data size unit")
    category: GraphCategory = Field(description="Traffic category")


class BaseUserQuery(BaseGraphQuery):
    """Base model for user-specific graph queries"""
    username: str = Field(default="", description="Username to filter by")
    username_enc: str = Field(default="", description="HTML-encoded username")
    operator: str = Field(description="Current operator user from session")
    title: str = Field(description="Page title from translation")
    help: str = Field(description="Help text from translation")
    log: str = Field(default="visited page: ", description="Basic log message")
    log_query: Optional[str] = Field(default=None, description="Query-specific log message")
    inline_extra_js: str = Field(default="", description="Inline JavaScript code")
    failure_msg: Optional[str] = Field(default=None, description="Error message when validation fails")
    img_format: str = Field(default='<div class="my-3 text-center"><img src="%s" alt="%s"></div>', description="HTML format for graph images")
    lang_code: Optional[str] = Field(default=None, description="Language code for page")
    
    @validator('username_enc', always=True)
    def encode_username(cls, v, values):
        """Encode username for HTML display"""
        if 'username' in values and values['username']:
            # In real implementation, this would use proper HTML encoding
            return values['username'].replace('%', '')
        return v
    
    @validator('log_query', always=True)
    def set_log_query(cls, v, values):
        """Set log query message if username and type are provided"""
        username = values.get('username', '')
        type_val = values.get('type')
        if username and type_val:
            return f"performed query for user [{username}] of type [{type_val}] on page: "
        return v
    
    @validator('failure_msg', always=True)
    def set_failure_msg(cls, v, values):
        """Set failure message if username is empty"""
        username = values.get('username', '')
        if not username:
            return "You must provide a valid username"
        return v


class BaseDateQuery(BaseGraphModel):
    """Base model for date-specific graph queries"""
    logged_users_on_date: date = Field(default_factory=lambda: date.today(), description="Date for logged users query")
    operator: str = Field(description="Current operator user from session")
    title: str = Field(description="Page title from translation")
    help: str = Field(description="Help text from translation") 
    log: str = Field(default="visited page: ", description="Basic log message")
    log_query: str = Field(description="Query-specific log message with date interval")
    img_format: str = Field(default='<div class="my-3 text-center"><img src="%s" alt="%s"></div>', description="HTML format for graph images")
    lang_code: Optional[str] = Field(default=None, description="Language code for page")
    
    @property
    def day(self) -> int:
        """Get day from date"""
        return self.logged_users_on_date.day
    
    @property
    def month(self) -> int:
        """Get month from date"""
        return self.logged_users_on_date.month
    
    @property
    def year(self) -> int:
        """Get year from date"""
        return self.logged_users_on_date.year
    
    @validator('log_query', always=True)
    def set_log_query(cls, v, values):
        """Set log query message with date interval"""
        date_val = values.get('logged_users_on_date')
        if date_val:
            return f"performed query on the following interval  [{date_val.day} - {date_val.month} - {date_val.year}] on page: "
        return "performed query on date interval on page: "


# Main page model - follows SRP principle

class GraphMainPageModel(BaseGraphModel):
    """Data model for graphs-main.php"""
    operator: str = Field(description="Current operator user from session")
    title: str = Field(description="Page title from translation")
    help: str = Field(description="Help text from translation")
    log: str = Field(default="visited page: ", description="Basic log message")
    lang_code: Optional[str] = Field(default=None, description="Language code for page")


# Overall traffic models - follows SRP and LSP principles

class OverallUploadModel(BaseUserQuery, BaseTrafficQuery):
    """Data model for graphs-overall_upload.php"""
    category: GraphCategory = Field(default=GraphCategory.UPLOAD, const=True)
    
    # Sidebar variables
    overall_upload_username: str = Field(default="", description="Username for sidebar")
    overall_upload_type: GraphType = Field(default=GraphType.DAILY, description="Type for sidebar")
    overall_upload_size: DataSize = Field(default=DataSize.MEGABYTES, description="Size for sidebar")
    
    # Chart-specific variables
    src: str = Field(default="", description="Graph source URL")
    alt: str = Field(default="", description="Graph alt text")
    
    # Navigation
    navkeys: List[List[str]] = Field(default=[['Graphs', 'Graphs'], ['Statistics', 'Statistics']], description="Navigation keys")
    button_id: str = Field(default="statistics-button", description="Button ID for JavaScript")
    
    @root_validator
    def sync_sidebar_vars_and_js(cls, values):
        """Synchronize sidebar variables with main parameters and set inline JS"""
        values['overall_upload_username'] = values.get('username_enc', '')
        values['overall_upload_type'] = values.get('type', GraphType.DAILY)
        values['overall_upload_size'] = values.get('size', DataSize.MEGABYTES)
        
        # Set chart URLs
        username_enc = values.get('username_enc', '')
        type_val = values.get('type', 'daily')
        size_val = values.get('size', 'megabytes')
        if username_enc:
            values['src'] = f"library/graphs/overall_users_data.php?category=upload&type={type_val}&size={size_val}&user={username_enc}"
            values['alt'] = f"traffic uploaded by user {username_enc}"
        
        # Set inline JavaScript if goto_stats is true
        goto_stats = values.get('goto_stats', False)
        if goto_stats:
            values['inline_extra_js'] = """
window.addEventListener('load', function() {
    document.getElementById('statistics-button').click();
});
"""
        return values


class OverallDownloadModel(BaseUserQuery, BaseTrafficQuery):
    """Data model for graphs-overall_download.php"""
    category: GraphCategory = Field(default=GraphCategory.DOWNLOAD, const=True)
    
    # Sidebar variables
    overall_download_username: str = Field(default="", description="Username for sidebar")
    overall_download_type: GraphType = Field(default=GraphType.DAILY, description="Type for sidebar")
    overall_download_size: DataSize = Field(default=DataSize.MEGABYTES, description="Size for sidebar")
    
    # Chart-specific variables
    src: str = Field(default="", description="Graph source URL")
    alt: str = Field(default="", description="Graph alt text")
    
    # Navigation
    navkeys: List[List[str]] = Field(default=[['Graphs', 'Graphs'], ['Statistics', 'Statistics']], description="Navigation keys")
    button_id: str = Field(default="statistics-button", description="Button ID for JavaScript")
    
    @root_validator
    def sync_sidebar_vars_and_js(cls, values):
        """Synchronize sidebar variables with main parameters and set inline JS"""
        values['overall_download_username'] = values.get('username_enc', '')
        values['overall_download_type'] = values.get('type', GraphType.DAILY)
        values['overall_download_size'] = values.get('size', DataSize.MEGABYTES)
        
        # Set chart URLs
        username_enc = values.get('username_enc', '')
        type_val = values.get('type', 'daily')
        size_val = values.get('size', 'megabytes')
        if username_enc:
            values['src'] = f"library/graphs/overall_users_data.php?category=download&type={type_val}&size={size_val}&user={username_enc}"
            values['alt'] = f"traffic downloaded by user {username_enc}"
        
        # Set inline JavaScript if goto_stats is true
        goto_stats = values.get('goto_stats', False)
        if goto_stats:
            values['inline_extra_js'] = """
window.addEventListener('load', function() {
    document.getElementById('statistics-button').click();
});
"""
        return values


class OverallLoginsModel(BaseUserQuery):
    """Data model for graphs-overall_logins.php"""
    # Sidebar variables
    overall_logins_username: str = Field(default="", description="Username for sidebar")
    overall_logins_type: GraphType = Field(default=GraphType.DAILY, description="Type for sidebar")
    
    # Chart-specific variables
    src: str = Field(default="", description="Graph source URL")
    alt: str = Field(default="", description="Graph alt text")
    
    # Navigation
    navkeys: List[List[str]] = Field(default=[['Graphs', 'Graphs'], ['Statistics', 'Statistics']], description="Navigation keys")
    button_id: str = Field(default="statistics-button", description="Button ID for JavaScript")
    
    @root_validator
    def sync_sidebar_vars_and_js(cls, values):
        """Synchronize sidebar variables with main parameters and set inline JS"""
        values['overall_logins_username'] = values.get('username_enc', '')
        values['overall_logins_type'] = values.get('type', GraphType.DAILY)
        
        # Set chart URLs
        username_enc = values.get('username_enc', '')
        type_val = values.get('type', 'daily')
        if username_enc:
            values['src'] = f"library/graphs/overall_users_data.php?category=login&type={type_val}&user={username_enc}"
            values['alt'] = f"{type_val.capitalize()} login/hit statistics for user {username_enc}"
        
        # Set inline JavaScript if goto_stats is true
        goto_stats = values.get('goto_stats', False)
        if goto_stats:
            values['inline_extra_js'] = """
window.addEventListener('load', function() {
    document.getElementById('statistics-button').click();
});
"""
        return values


# Logged users model - follows SRP principle

class LoggedUsersModel(BaseDateQuery):
    """Data model for graphs-logged_users.php"""
    
    # Chart source URLs and alt text
    daily_src: str = Field(default="", description="Daily chart source URL")
    daily_alt: str = Field(default="", description="Daily chart alt text")
    monthly_src: str = Field(default="", description="Monthly chart source URL") 
    monthly_alt: str = Field(default="", description="Monthly chart alt text")
    
    # Navigation
    navkeys: List[List[str]] = Field(default=[['Daily', 'Daily Chart'], ['Monthly', 'Monthly Chart']], description="Navigation keys")
    
    def get_daily_chart_params(self) -> Dict[str, int]:
        """Get parameters for daily chart"""
        return {
            'day': self.day,
            'month': self.month,
            'year': self.year
        }
    
    def get_monthly_chart_params(self) -> Dict[str, int]:
        """Get parameters for monthly chart"""
        return {
            'month': self.month,
            'year': self.year
        }
    
    @root_validator
    def set_chart_urls(cls, values):
        """Set chart source URLs and alt text"""
        date_val = values.get('logged_users_on_date')
        if date_val:
            day = date_val.day
            month = date_val.month
            year = date_val.year
            
            # Daily chart
            values['daily_src'] = f"library/graphs/logged_users.php?day={day:02d}&month={month:02d}&year={year:04d}"
            values['daily_alt'] = f"user accounted per-hour on the {year:04d}-{month:02d}-{day:02d}"
            
            # Monthly chart
            values['monthly_src'] = f"library/graphs/logged_users.php?month={month:02d}&year={year:04d}"
            values['monthly_alt'] = f"min/max user accounted per-day in the month {month:02d}-{year:04d}"
            
        return values


# All-time models - follows SRP and OCP principles

class AlltimeLoginsModel(BaseGraphQuery):
    """Data model for graphs-alltime_logins.php"""
    operator: str = Field(description="Current operator user from session")
    title: str = Field(description="Page title from translation")
    help: str = Field(description="Help text from translation")
    log: str = Field(default="visited page: ", description="Basic log message")
    log_query: str = Field(description="Query-specific log message")
    inline_extra_js: str = Field(default="", description="Inline JavaScript code")
    img_format: str = Field(default='<div class="my-3 text-center"><img src="%s" alt="%s"></div>', description="HTML format for graph images")
    lang_code: Optional[str] = Field(default=None, description="Language code for page")
    
    # Sidebar variables
    alltime_login_type: GraphType = Field(default=GraphType.DAILY, description="Login type for sidebar")
    
    # Chart-specific variables
    src: str = Field(default="", description="Graph source URL")
    alt: str = Field(default="", description="Graph alt text")
    
    # Navigation
    navkeys: List[List[str]] = Field(default=[['Graphs', 'Graphs'], ['Statistics', 'Statistics']], description="Navigation keys")
    button_id: str = Field(default="statistics-button", description="Button ID for JavaScript")
    
    @validator('log_query', always=True)
    def set_log_query(cls, v, values):
        """Set log query message with type"""
        type_val = values.get('type', 'daily')
        return f"performed query of type [{type_val}] on page: "
    
    @root_validator
    def sync_sidebar_vars(cls, values):
        """Synchronize sidebar variables with main parameters"""
        values['alltime_login_type'] = values.get('type', GraphType.DAILY)
        
        # Set chart URLs
        type_val = values.get('type', 'daily')
        values['src'] = f"library/graphs/alltime_users_data.php?category=login&type={type_val}"
        values['alt'] = f"{type_val.capitalize()} all-time login/hit statistics"
        
        return values
    
    @root_validator  
    def set_inline_js(cls, values):
        """Set inline JavaScript if goto_stats is true"""
        goto_stats = values.get('goto_stats', False)
        if goto_stats:
            values['inline_extra_js'] = """
window.addEventListener('load', function() {
    document.getElementById('statistics-button').click();
});
"""
        return values


class AlltimeTrafficCompareModel(BaseTrafficQuery):
    """Data model for graphs-alltime_traffic_compare.php"""
    # Remove category field as this model handles both upload and download
    category: Optional[GraphCategory] = Field(default=None)
    operator: str = Field(description="Current operator user from session")
    title: str = Field(description="Page title from translation")
    help: str = Field(description="Help text from translation")
    log: str = Field(default="visited page: ", description="Basic log message")
    log_query: str = Field(description="Query-specific log message")
    img_format: str = Field(default='<div class="my-3 text-center"><img src="%s" alt="%s"></div>', description="HTML format for graph images")
    lang_code: Optional[str] = Field(default=None, description="Language code for page")
    
    # Sidebar variables
    traffic_compare_type: GraphType = Field(default=GraphType.DAILY, description="Type for sidebar")
    traffic_compare_size: DataSize = Field(default=DataSize.MEGABYTES, description="Size for sidebar")
    
    # Chart-specific variables
    download_src: str = Field(default="", description="Download chart source URL")
    download_alt: str = Field(default="", description="Download chart alt text")
    upload_src: str = Field(default="", description="Upload chart source URL")
    upload_alt: str = Field(default="", description="Upload chart alt text")
    
    # Navigation
    navkeys: List[List[str]] = Field(default=[['Download', 'Download Chart'], ['Upload', 'Upload Chart']], description="Navigation keys")
    
    @validator('log_query', always=True)
    def set_log_query(cls, v, values):
        """Set log query message with type and size"""
        type_val = values.get('type', 'daily')
        size_val = values.get('size', 'megabytes')
        return f"performed query of type [{type_val}] and size [{size_val}] on page: "
    
    @root_validator
    def sync_sidebar_vars(cls, values):
        """Synchronize sidebar variables with main parameters"""
        values['traffic_compare_type'] = values.get('type', GraphType.DAILY)
        values['traffic_compare_size'] = values.get('size', DataSize.MEGABYTES)
        return values
    
    @root_validator
    def set_chart_urls(cls, values):
        """Set chart source URLs and alt text"""
        type_val = values.get('type', 'daily')
        size_val = values.get('size', 'megabytes')
        
        # Download chart
        values['download_src'] = f"library/graphs/alltime_users_data.php?category=download&type={type_val}&size={size_val}"
        values['download_alt'] = f"{type_val.capitalize()} all-time download traffic (in {size_val}) statistics"
        
        # Upload chart  
        values['upload_src'] = f"library/graphs/alltime_users_data.php?category=upload&type={type_val}&size={size_val}"
        values['upload_alt'] = f"{type_val.capitalize()} all-time upload traffic (in {size_val}) statistics"
        
        return values


# Graph data source models - follows DIP principle (abstraction layer)

class GraphDataSource(BaseGraphModel):
    """Base model for graph data sources"""
    src: str = Field(description="Source URL for graph image")
    alt: str = Field(description="Alt text for graph image")


class OverallUsersDataSource(GraphDataSource):
    """Data source model for overall users data graphs"""
    category: GraphCategory = Field(description="Data category")
    type: GraphType = Field(description="Time period type")
    size: Optional[DataSize] = Field(default=None, description="Data size unit")
    user: str = Field(default="", description="Username filter")
    
    def __init__(self, **data):
        # Generate src URL based on parameters
        if 'src' not in data:
            size_param = f"&size={data.get('size', '')}" if data.get('size') else ""
            user_param = f"&user={data.get('user', '')}" if data.get('user') else ""
            data['src'] = f"library/graphs/overall_users_data.php?category={data.get('category', '')}&type={data.get('type', '')}{size_param}{user_param}"
        
        # Generate alt text based on parameters
        if 'alt' not in data:
            category = data.get('category', '')
            user = data.get('user', '')
            if category == 'login':
                data['alt'] = f"{data.get('type', '').capitalize()} login/hit statistics for user {user}"
            else:
                data['alt'] = f"traffic {category} by user {user}"
        
        super().__init__(**data)


class AlltimeUsersDataSource(GraphDataSource):
    """Data source model for all-time users data graphs"""
    category: GraphCategory = Field(description="Data category")
    type: GraphType = Field(description="Time period type")
    size: Optional[DataSize] = Field(default=None, description="Data size unit")
    
    def __init__(self, **data):
        # Generate src URL based on parameters
        if 'src' not in data:
            size_param = f"&size={data.get('size', '')}" if data.get('size') else ""
            data['src'] = f"library/graphs/alltime_users_data.php?category={data.get('category', '')}&type={data.get('type', '')}{size_param}"
        
        # Generate alt text based on parameters
        if 'alt' not in data:
            category = data.get('category', '')
            type_str = data.get('type', '').capitalize()
            size = data.get('size', '')
            if category == 'login':
                data['alt'] = f"{type_str} all-time login/hit statistics"
            else:
                data['alt'] = f"{type_str} all-time {category} traffic (in {size}) statistics"
        
        super().__init__(**data)


class LoggedUsersDataSource(GraphDataSource):
    """Data source model for logged users graphs"""
    day: Optional[int] = Field(default=None, description="Day parameter")
    month: int = Field(description="Month parameter")
    year: int = Field(description="Year parameter")
    
    def __init__(self, **data):
        # Generate src URL based on parameters
        if 'src' not in data:
            if data.get('day') is not None:
                # Daily chart
                data['src'] = f"library/graphs/logged_users.php?day={data.get('day'):02d}&month={data.get('month'):02d}&year={data.get('year'):04d}"
                data['alt'] = f"user accounted per-hour on the {data.get('year'):04d}-{data.get('month'):02d}-{data.get('day'):02d}"
            else:
                # Monthly chart
                data['src'] = f"library/graphs/logged_users.php?month={data.get('month'):02d}&year={data.get('year'):04d}"
                data['alt'] = f"min/max user accounted per-day in the month {data.get('month'):02d}-{data.get('year'):04d}"
        
        super().__init__(**data)


# Navigation models - follows ISP principle

class NavKey(BaseGraphModel):
    """Model for navigation key pairs"""
    key: str = Field(description="Navigation key")
    label: str = Field(description="Navigation label")


class TabNavigation(BaseGraphModel):
    """Model for tab navigation structure"""
    navkeys: List[NavKey] = Field(description="List of navigation keys")
    active_tab: int = Field(default=0, description="Index of active tab")


# Logging models - follows SRP principle

class GraphLogEntry(BaseGraphModel):
    """Model for graph-related log entries"""
    log: str = Field(description="Basic log message")
    log_query: Optional[str] = Field(default=None, description="Query-specific log message")
    username: Optional[str] = Field(default=None, description="Username in log")
    type: Optional[GraphType] = Field(default=None, description="Query type in log")
    size: Optional[DataSize] = Field(default=None, description="Data size in log")
    date_params: Optional[Dict[str, int]] = Field(default=None, description="Date parameters in log")


# Composite models for complete page data - follows SRP and composition principles

class GraphPageData(BaseGraphModel):
    """Base model for complete graph page data"""
    title: str = Field(description="Page title")
    help: str = Field(description="Help text")
    operator: str = Field(description="Current operator")
    navigation: Optional[TabNavigation] = Field(default=None, description="Tab navigation")
    log_entry: GraphLogEntry = Field(description="Log entry for this page")


class OverallGraphPageData(GraphPageData):
    """Complete page data for overall graphs"""
    query_params: Union[OverallUploadModel, OverallDownloadModel, OverallLoginsModel] = Field(description="Query parameters")
    data_source: OverallUsersDataSource = Field(description="Graph data source")
    show_content: bool = Field(description="Whether to show graph content")


class AlltimeGraphPageData(GraphPageData):
    """Complete page data for all-time graphs"""
    query_params: Union[AlltimeLoginsModel, AlltimeTrafficCompareModel] = Field(description="Query parameters")
    data_sources: List[AlltimeUsersDataSource] = Field(description="Graph data sources")


class LoggedUsersPageData(GraphPageData):
    """Complete page data for logged users graphs"""
    query_params: LoggedUsersModel = Field(description="Query parameters")
    daily_data_source: LoggedUsersDataSource = Field(description="Daily chart data source")
    monthly_data_source: LoggedUsersDataSource = Field(description="Monthly chart data source")


# Factory classes for creating models - follows Factory pattern and DIP

class GraphModelFactory:
    """Factory for creating graph models - follows DIP principle"""
    
    @staticmethod
    def create_overall_upload(username: str = "", type: str = "daily", size: str = "megabytes", goto_stats: bool = False) -> OverallUploadModel:
        """Create overall upload model"""
        return OverallUploadModel(
            username=username,
            type=GraphType(type),
            size=DataSize(size),
            goto_stats=goto_stats
        )
    
    @staticmethod
    def create_overall_download(username: str = "", type: str = "daily", size: str = "megabytes", goto_stats: bool = False) -> OverallDownloadModel:
        """Create overall download model"""
        return OverallDownloadModel(
            username=username,
            type=GraphType(type),
            size=DataSize(size),
            goto_stats=goto_stats
        )
    
    @staticmethod
    def create_overall_logins(username: str = "", type: str = "daily", goto_stats: bool = False) -> OverallLoginsModel:
        """Create overall logins model"""
        return OverallLoginsModel(
            username=username,
            type=GraphType(type),
            goto_stats=goto_stats
        )
    
    @staticmethod
    def create_logged_users(logged_users_on_date: date = None) -> LoggedUsersModel:
        """Create logged users model"""
        if logged_users_on_date is None:
            logged_users_on_date = date.today()
        return LoggedUsersModel(logged_users_on_date=logged_users_on_date)
    
    @staticmethod
    def create_alltime_logins(type: str = "daily", goto_stats: bool = False) -> AlltimeLoginsModel:
        """Create all-time logins model"""
        return AlltimeLoginsModel(
            type=GraphType(type),
            goto_stats=goto_stats
        )
    
    @staticmethod
    def create_alltime_traffic_compare(type: str = "daily", size: str = "megabytes") -> AlltimeTrafficCompareModel:
        """Create all-time traffic compare model"""
        return AlltimeTrafficCompareModel(
            type=GraphType(type),
            size=DataSize(size)
        )


# Utility classes - follows utility pattern

class GraphUtils:
    """Utility functions for graph operations"""
    
    @staticmethod
    def generate_image_format() -> str:
        """Generate HTML format string for graph images"""
        return '<div class="my-3 text-center"><img src="%s" alt="%s"></div>'
    
    @staticmethod
    def validate_date_regex(date_str: str) -> bool:
        """Validate date string format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def create_nav_keys(keys: List[tuple]) -> List[NavKey]:
        """Create navigation keys from tuples"""
        return [NavKey(key=key, label=label) for key, label in keys]
    
    @staticmethod
    def generate_inline_js(button_id: str) -> str:
        """Generate inline JavaScript for tab switching"""
        return f"""
window.addEventListener('load', function() {{
    document.getElementById('{button_id}').click();
}});
"""


# Error handling models - follows SRP principle

class GraphError(BaseGraphModel):
    """Model for graph-related errors"""
    error_type: str = Field(description="Type of error")
    message: str = Field(description="Error message")
    field: Optional[str] = Field(default=None, description="Field that caused error")


class GraphValidationError(GraphError):
    """Model for validation errors in graph parameters"""
    invalid_value: Any = Field(description="The invalid value")
    valid_options: List[str] = Field(description="List of valid options")


# Configuration models - follows SRP principle

class GraphConfig(BaseGraphModel):
    """Configuration model for graph settings"""
    default_type: GraphType = Field(default=GraphType.DAILY, description="Default graph type")
    default_size: DataSize = Field(default=DataSize.MEGABYTES, description="Default data size")
    image_format: str = Field(default='<div class="my-3 text-center"><img src="%s" alt="%s"></div>', description="HTML format for images")
    date_regex: str = Field(default=r'(\d{4})-(\d{2})-(\d{2})', description="Regex for date validation")


# Export all models for easy importing
__all__ = [
    # Base models
    'BaseGraphModel', 'BaseGraphQuery', 'BaseTrafficQuery', 'BaseUserQuery', 'BaseDateQuery',
    
    # Enums
    'GraphType', 'DataSize', 'GraphCategory', 'ChartType',
    
    # Main models
    'GraphMainPageModel', 'OverallUploadModel', 'OverallDownloadModel', 'OverallLoginsModel',
    'LoggedUsersModel', 'AlltimeLoginsModel', 'AlltimeTrafficCompareModel',
    
    # Data source models
    'GraphDataSource', 'OverallUsersDataSource', 'AlltimeUsersDataSource', 'LoggedUsersDataSource',
    
    # Navigation models
    'NavKey', 'TabNavigation',
    
    # Logging models
    'GraphLogEntry',
    
    # Composite models
    'GraphPageData', 'OverallGraphPageData', 'AlltimeGraphPageData', 'LoggedUsersPageData',
    
    # Factory and utilities
    'GraphModelFactory', 'GraphUtils',
    
    # Error models
    'GraphError', 'GraphValidationError',
    
    # Configuration
    'GraphConfig'
]