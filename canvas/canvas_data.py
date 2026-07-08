from dataclasses import dataclass
import pyvista as pv
import vtk


@dataclass
class NodeActors:
    point_actor: vtk.vtkActor
    point_mesh: pv.PolyData
    label_actor: vtk.vtkActor2D
    label_mesh: pv.PolyData

@dataclass
class BeamActors:
    beam_actor: vtk.vtkActor
    beam_mesh: pv.PolyData