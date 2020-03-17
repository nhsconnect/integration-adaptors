"""A module that provides functions to generate tags suitable for identifying specific CI/CD builds."""

import argparse


def generate_tag(branch_name: str, build_id: str, git_hash: str) -> str:
    """Generate a build tag from the provided values.

    :param branch_name: The name of the branch this build is being performed for.
    :param build_id: The identifier of the build being performed.
    :param git_hash: Git hash of the commit used.
    :return: A string that represents the build being performed.
    """
    clean_branch_name = _clean_tag_element(branch_name)
    clean_build_id = _clean_tag_element(build_id)

    tag = "-".join([clean_branch_name, clean_build_id, git_hash[:7]])
    return tag


def _clean_tag_element(tag_element: str) -> str:
    clean_tag_element = tag_element.replace("/", "-")
    return clean_tag_element


def _parse_arguments():
    parser = argparse.ArgumentParser(description="Generates a tag suitable for identifying a specific CI/CD build.")

    parser.add_argument("branch_name", help="The name of the branch this build is being performed for.")
    parser.add_argument("build_id", help="The identifier of the build being performed.")
    parser.add_argument("git_hash", help="The git hash of commit used.")

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()

    print(generate_tag(args.branch_name, args.build_id, args.git_hash), end="")
