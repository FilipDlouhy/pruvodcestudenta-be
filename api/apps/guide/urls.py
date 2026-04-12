from rest_framework.routers import SimpleRouter

from .controllers.landing import LandingController
from .controllers.sections import SectionController
from .controllers.topics import TopicController

router = SimpleRouter(trailing_slash=False)
router.register("pages/landing", LandingController, basename="landing")
router.register("pages/sections", SectionController, basename="section")
router.register("pages/topics", TopicController, basename="topic")

urlpatterns = router.urls
