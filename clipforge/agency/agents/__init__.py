from .business import BusinessAgent
from .captioner import CaptionAgent
from .clipper import ClipperAgent
from .intake import IntakeAgent
from .publisher import PublishingAgent
from .quality import QualityAgent
from .research import ResearchAgent
from .sales import SalesAgent
from .strategist import StrategistAgent

# Order = pipeline order shown on the dashboard.
ALL = [ResearchAgent, SalesAgent, IntakeAgent, StrategistAgent, ClipperAgent,
       CaptionAgent, QualityAgent, PublishingAgent, BusinessAgent]
