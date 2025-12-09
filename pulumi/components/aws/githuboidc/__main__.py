from pulumi.provider.experimental import component_provider_host
from githuboidc import Githuboidc

if __name__ == "__main__":
    component_provider_host(name="githuboidc", components=[Githuboidc])
