from _mandatory_requirement import MandatoryRequirement

class VideoPlusIfMoreThanOneCamera(MandatoryRequirement):
    def check(self):
        if self.total_quantities['CAMERA'] > 1 and not self.total_quantities['VIDEOPLUS']:
            self.add_mandatory_product('VIDEOPLUS', 1)