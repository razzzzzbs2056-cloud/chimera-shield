from .business import BusinessAgent
from .captioner import CaptionAgent
from .clipper import ClipperAgent
from .editors import AudioEngineer, MotionEditor, PacingEditor
from .filmcraft_agents import FilmCraftAssembler, FilmCraftColorist, FilmCraftFinisher
from .intake import IntakeAgent
from .publisher import PublishingAgent
from .quality import QualityAgent
from .research import ResearchAgent
from .sales import SalesAgent
from .strategist import StrategistAgent

# Order = pipeline order shown on the dashboard.
ALL = [ResearchAgent, SalesAgent, IntakeAgent, StrategistAgent, ClipperAgent,
       PacingEditor, MotionEditor, AudioEngineer, CaptionAgent,
       FilmCraftAssembler, FilmCraftColorist, FilmCraftFinisher, QualityAgent, PublishingAgent, BusinessAgent]
