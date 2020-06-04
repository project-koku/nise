import os

from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.azure.generator import AzureGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator


def ocp_label_splitter(label):
    return [kv.split(":") for kv in [lab.split("_")[1] for lab in label.split("|")]]


def get_resourceid_and_tags(data):
    id_labels = {}
    for resource_id, tags in data.resourceid_labels.items():
        id_labels[resource_id] = [ocp_label_splitter(label) for label in tags]
    return id_labels


def get_validated_config(gen, args):
    config = gen.init_config(args)
    gen.validate_config(config)
    return config


def run_generator(gen, args, config=None):
    if not config:
        config = gen.init_config(args)
    return gen.process_template(args, config)


class OCPonXGenerator:
    def __init__(self):
        self.aws = AWSGenerator
        self.azure = AzureGenerator
        self.ocp = OCPGenerator()

    def init_config(self, args):
        return

    def process_template(self, args, config):
        from nise.yaml_gen import STATIC_DIR

        # First OCP:
        args.provider = "ocp"
        args.template_file_name = os.path.join(STATIC_DIR, "ocp_static_data.yml.j2")
        args.config_file_name = os.path.join(STATIC_DIR, "ocp_generator_config.yml")
        args.output_file_name = "ocp_aws_ocp.yml"
        config = get_validated_config(self.ocp, args)
        data = run_generator(self.ocp, args, config)
        id_labels = get_resourceid_and_tags(data)

        # AWS:
        args.provider = "aws"
        args.output_file_name = "ocp_aws_aws.yml"
        args.template_file_name = os.path.join(STATIC_DIR, "aws_static_data.yml.j2")
        args.config_file_name = os.path.join(STATIC_DIR, "aws_generator_config.yml")
        self.aws = self.aws(id_labels)
        config = get_validated_config(self.aws, args)
        run_generator(self.aws, args, config)

        # Second OCP:
        args.provider = "ocp"
        args.output_file_name = "ocp_azure_ocp.yml"
        args.template_file_name = os.path.join(STATIC_DIR, "ocp_static_data.yml.j2")
        args.config_file_name = os.path.join(STATIC_DIR, "ocp_generator_config.yml")
        config = get_validated_config(self.ocp, args)
        data = run_generator(self.ocp, args, config)
        id_labels = get_resourceid_and_tags(data)

        # Azure
        args.provider = "azure"
        args.output_file_name = "ocp_azure_azure.yml"
        args.template_file_name = os.path.join(STATIC_DIR, "azure_static_data.yml.j2")
        args.config_file_name = os.path.join(STATIC_DIR, "azure_generator_config.yml")
        self.azure = self.azure(id_labels)
        config = get_validated_config(self.azure, args)
        run_generator(self.azure, args, config)
