from core.database import Base, engine

# Import ALL models here
from models.waitlist import WaitlistUser
from models.analytics_event import AnalyticsEvent
print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")