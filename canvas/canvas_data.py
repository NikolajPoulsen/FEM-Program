import pyvista as pv
import vtk

from dataclasses import dataclass

@dataclass
class NodeActors:
    point_actor: vtk.vtkActor
    point_mesh: pv.PolyData
    label_actor: vtk.vtkActor
    label_mesh: pv.PolyData

@dataclass
class BeamActors:
    beam_actor: vtk.vtkActor
    beam_mesh: pv.PolyData

@dataclass
class ConstraintActors:
    actor: vtk.vtkActor
    mesh: pv.PolyData
    c_type: str  # 'fixed', 'pinned' eller 'roller'

@dataclass
class LoadActors:
    actor: vtk.vtkActor
    mesh: pv.PolyData
    l_type: str  # 'point_load' eller 'line_load'