from pulumi.provider.experimental import component_provider_host
from vpc import Vpc

if __name__ == "__main__":
    component_provider_host(name="vpc", components=[Vpc])
