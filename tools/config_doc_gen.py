from skywalking.config import options_with_default_value_and_type

doc_head = """# Supported Agent Configuration Options

Below is the full list of supported configurations you can set to
customize the agent behavior, please read the descriptions for what they can achieve.

> Usage: (Pass in intrusive setup)
```
from skywalking import config, agent
config.init(configuration=YourValue))
agent.start()
```
> Usage: (Pass by environment variables)
```
export SW_AGENT_YourConfiguration=YourValue
```

"""
table_head = """### {}
| Configuration | Environment Variable | Type | Default Value | Description |
| :------------ | :------------ | :------------ | :------------ | :------------ |
"""


def comments_from_file(file_path):
    comments = []
    analyze = False
    comment_block_begin = False
    with open(file_path, 'r') as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]
        for line in lines:
            if line.startswith('# THIS MUST PRECEDE DIRECTLY BEFORE LIST OF CONFIG OPTIONS!'):
                analyze = True
                continue
            elif line.startswith('# THIS MUST FOLLOW DIRECTLY AFTER LIST OF CONFIG OPTIONS!'):
                break
            if analyze and line.startswith('#'):
                if line.startswith('# BEGIN'):
                    comments.append(line)
                    comment_block_begin = False
                    continue
                if comment_block_begin:
                    comments[-1] += line.lstrip('#')
                    continue
                comment_block_begin = True
                comments.append(line.lstrip('# '))
            else:  # not comment
                if comment_block_begin:
                    comment_block_begin = False
        return comments


def create_entry(comment: str, config_index: int) -> str:
    """
    Each configuration entry is matched with comment (blocks) by index
    Args:
        comment:
        config_index:

    Returns:

    """
    def env_var_name(config_entry):
        return 'SW_AGENT_' + config_entry.upper()

    configuration = list(options_with_default_value_and_type.keys())[config_index]
    type_ = options_with_default_value_and_type[configuration][1]
    default_val = options_with_default_value_and_type[configuration][0]

    return f'| {configuration} | {env_var_name(configuration)} | {str(type_)} | {default_val} | {comment} |'


def generate_markdown_table():
    comments = comments_from_file('skywalking/config.py')

    with open('docs/en/setup/Configuration.md', 'w') as plugin_doc:
        plugin_doc.write(doc_head)
        offset = 0
        for config_index, comment in enumerate(comments):
            if comment.startswith('# BEGIN'):
                plugin_doc.write(table_head.format(comment.lstrip('# ')))
                offset += 1
            else:
                table_entry = create_entry(comment, config_index - offset)
                plugin_doc.write(f'{table_entry}\n')


if __name__ == '__main__':
    generate_markdown_table()
