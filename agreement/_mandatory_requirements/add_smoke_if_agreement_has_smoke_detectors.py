from _mandatory_requirement import MandatoryRequirement

class SmokeServiceIffAgreementHasSmokeDetectors(MandatoryRequirement):
    def check(self):
        if self.total_quantities['WSMOKE'] > 0 and not self.total_quantities['SMOKE']:
            self.add_mandatory_product('SMOKE', 1)

