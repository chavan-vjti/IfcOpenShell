import uuid
import time
import tempfile
import ifcopenshell
import operator
import math
O = 0., 0., 0.
X = 1., 0., 0.
Y = 0., 1., 0.
Z = 0., 0., 1.

R = 16.0
H = 10.0

# Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
def create_ifcaxis2placement(ifcfile, point, dir1, dir2):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

# Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile, point, dir1, dir2)
    ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to, axis2placement)
    return ifclocalplacement2


# Creates an IfcPolyLine from a list of points, specified as Python tuples
def create_ifcpolyline(ifcfile, point_list):
    ifcpts = []
    for point in point_list:
        point = ifcfile.createIfcCartesianPoint(point)
        ifcpts.append(point)
    polyline = ifcfile.createIfcPolyLine(ifcpts)
    return polyline


# Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
def create_ifcextrudedareasolid(ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
    polyline = create_ifcpolyline(ifcfile, point_list)
    ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    ifcdir = ifcfile.createIfcDirection(extrude_dir)
    ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
    return ifcextrudedareasolid

def getPoint(theta):
    theta = math.radians(theta)
    x = (R * math.cos(theta), 0.0, 0.0)
    y = (0.0, R * math.sin(theta), 0.0)
    # point = (R * math.cos(theta)) * numpy.array([1.0, 0.0, 0.0]) + (R * math.sin(theta)) * numpy.array([0.0, 1.0, 0.0])
    point = tuple(sum(i) for i in zip(x, y))
    # point = x + y
    # point = (R * math.cos(theta)), 0.0, 0.0) + (0.0, R * math.cos(theta)), 0.0, 0.0)
    return point

def compute_params():
    # self.vDir = numpy.cross(self.wDir, self.uDir)
    a1 = getPoint(0)
    a2 = getPoint(60)
    a3 = getPoint(120)
    a4 = getPoint(180)
    a5 = getPoint(240)
    a6 = getPoint(300)
    return a1, a2, a3, a4, a5, a6, a1

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

# IFC template creation

filename = "Nut.ifc"
timestamp = time.time()
timestring = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(timestamp))
creator = "S. Chavan"
organization = "IIT Bombay"
application, application_version = "IfcOpenShell", "0.5"
project_globalid, project_name = create_guid(), "Osdag"

# A template IFC file to quickly populate entity instances for an IfcProject with its dependencies
template = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('%(filename)s','%(timestring)s',('%(creator)s'),('%(organization)s'),'%(application)s','%(application)s','');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;
DATA;
#1=IFCPERSON($,$,'%(creator)s',$,$,$,$,$);
#2=IFCORGANIZATION($,'%(organization)s',$,$,$);
#3=IFCPERSONANDORGANIZATION(#1,#2,$);
#4=IFCAPPLICATION(#2,'%(application_version)s','%(application)s','');
#5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,#3,#4,%(timestamp)s);
#6=IFCDIRECTION((1.,0.,0.));
#7=IFCDIRECTION((0.,0.,1.));
#8=IFCCARTESIANPOINT((0.,0.,0.));
#9=IFCAXIS2PLACEMENT3D(#8,#7,#6);
#10=IFCDIRECTION((0.,1.,0.));
#11=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#9,#10);
#12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
#13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
#15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
#16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
#17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
#18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
#19=IFCUNITASSIGNMENT((#13,#14,#15,#18));
#20=IFCPROJECT('%(project_globalid)s',#5,'%(project_name)s',$,$,$,$,(#11),#19);
ENDSEC;
END-ISO-10303-21;
""" % locals()

# Write the template to a temporary file
temp_handle, temp_filename = tempfile.mkstemp(suffix=".ifc")
with open(temp_filename, "wb") as f:
    f.write(template)

# Obtain references to instances defined in template
ifcfile = ifcopenshell.open(temp_filename)
owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
project = ifcfile.by_type("IfcProject")[0]
context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]

# IFC hierarchy creation
site_placement = create_ifclocalplacement(ifcfile)
site = ifcfile.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)

building_placement = create_ifclocalplacement(ifcfile, relative_to=site_placement)
building = ifcfile.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)

storey_placement = create_ifclocalplacement(ifcfile, relative_to=building_placement)
elevation = 0.0
building_storey = ifcfile.createIfcBuildingStorey(create_guid(), owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)

container_storey = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
container_site = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
container_project = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Project Container", None, project, [site])

# Beam creation: Define the beam shape as a polyline axis and an extruded area solid
beam_placement = create_ifclocalplacement(ifcfile, relative_to=storey_placement)
polyline = create_ifcpolyline(ifcfile, [(0.0, 0.0, 0.0), (R, 0.0, 0.0)])
axis_representation = ifcfile.createIfcShapeRepresentation(context, "Axis", "Curve2D", [polyline])

extrusion_placement = create_ifcaxis2placement(ifcfile, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
point_list_extrusion_area = compute_params()
solid = create_ifcextrudedareasolid(ifcfile, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), H)
body_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])

product_shape = ifcfile.createIfcProductDefinitionShape(None, None, [axis_representation, body_representation])

beam = ifcfile.createIfcWallStandardCase(create_guid(), owner_history, "Bolt " + str(int(R)), "An awesome beam",
                                         None, beam_placement,product_shape, None)
ifcfile.write(filename)
