import pystache
from pystache import TemplateSpec

from pystache.tests.examples import simple
from pystache import Renderer

renderer = Renderer()

hash = {
    'variable': 'qweqwe', 
    #'recordTarget.Patient.Id': '2.16.840.1.113883.2.1.4.1'
    'recordTarget': {
        'Patient': {
            'Id': '2.16.840.1.113883.2.1.4.1'
         }
     }
}

print(renderer.render_path('GpSummary.mustache', hash))

#renderer.render_path('layout.mustache', {'name': 'Did this actually work, if it did that would be sick'})


# class Example(TemplateSpec):

#     template_rel_path = 'example.mustache'
#     _weirdVariableName = None

#     def weirdVariableName(self):
#         return self._weirdVariableName



# render = Renderer()
# view = Example()
# view.weirdVariableName = "I can now build this however I want"

# print(render.render(view))


    
