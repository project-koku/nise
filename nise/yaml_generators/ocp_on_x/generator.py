from nise.yaml_generators.ocp.generator import OCPGenerator


def label_splitter(label):
    return [kv.split(":") for kv in [l.split("_")[1] for l in label.split("|")]]


class OCPonXGenerator(OCPGenerator):
    def do_something(self):
        return
