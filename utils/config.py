import yaml


class Config:
    """Object to store the email configuration."""

    def __init__(self, config_file='config.yml'):
        """Initialize the config object.

        Params
        ------
        config_file : str
            Path to the configuration file.
        """

        with open(config_file, 'r', encoding='utf-8') as yaml_data:
            try:
                self.config = yaml.safe_load(yaml_data)
            except yaml.YAMLError as exc:
                print(exc)

    def get_config(self):
        """Return the configuration as a dictionary."""

        return self.config
