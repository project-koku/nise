from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.azure.generator import AzureGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator


def ocp_label_splitter(label):
    return [kv.split(":") for kv in [l.split("_")[1] for l in label.split("|")]]


def get_resourceid_and_tags(data):
    id_labels = {}
    for resource_id, tags in data.resourceid_labels.items():
        id_labels[resource_id] = [ocp_label_splitter(label) for label in tags]
    return id_labels


def get_validated_config(gen, args):
    return gen.validate_config(gen.init_config(args))


def get_data(gen, args, config):
    return gen.build_data(config, args.random)


class OCPonXGenerator:
    def __init__(self):
        self.aws = AWSGenerator()
        self.azure = AzureGenerator()
        self.ocp = OCPGenerator()

    def init_config(self, args):
        return

    def process_template(self, args, config):

        config = get_validated_config(self.ocp, args)
        get_data(self.ocp, args, config)
