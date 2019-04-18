"""A simple script to test the use of a PystacheMessageBuilder."""

from mhs.builder.pystachemessagebuilder import PystacheMessageBuilder

builder = PystacheMessageBuilder("templates", "ebxml")
message = builder.build_message({})

print(message)
