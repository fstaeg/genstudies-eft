from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel


class EFTModel(PhysicsModel):
    def setPhysicsOptions(self, physOptions):
        self.pois = []
        self.quadratic = True
        for po in physOptions:
            if po.startswith("poi="):
                self.pois.extend(po.replace("poi=", "").split(":"))
            if po == "linear":
                self.quadratic = False

    def doParametersOfInterest(self):
        """Create POI and other parameters, and define the POI set."""
        for poi in self.pois:
            self.modelBuilder.doVar("%s[0,-1.0,1.0]" % poi)
            if self.quadratic:
                self.modelBuilder.factory_("prod::%s_quad(%s,%s)" % (poi,poi,poi))
        self.modelBuilder.doSet("POI", ",".join(self.pois))

    def getYieldScale(self, bin, process):
        "Return the name of a RooAbsReal to scale this yield by or the two special values 1 and 0 (don't scale, and set to zero)"
        for poi in self.pois:
            if process == "%s_lin" % poi:
                print("Scaling %s/%s by %s" % (bin, process, poi))
                return poi
            elif process == "%s_quad" % poi:
                if self.quadratic:
                    print("Scaling %s/%s by %s^2" % (bin, process, poi))
                    return "%s_quad" % poi
                else:
                    return 0
        else:
            return 1


eftModel = EFTModel()