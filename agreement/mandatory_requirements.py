from handy.reflector import Reflector
import _mandatory_requirements
from _mandatory_requirements._mandatory_requirement import MandatoryRequirement

MandatoryRequirements = Reflector(kls=MandatoryRequirement, source_package=_mandatory_requirements)

for name, kls in MandatoryRequirements.iteritems():
    locals()[name] = kls
