from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

from fdtdx.core.config import SimulationConfig
from fdtdx.objects.boundaries.perfectly_matched_layer import PerfectlyMatchedLayer
from fdtdx.objects.container import ObjectContainer
from fdtdx.objects.object import SimulationObject


def plot_setup(
    config: SimulationConfig,
    objects: ObjectContainer,
    exclude_object_list: list[SimulationObject] = [],
    filename: str | Path | None = None,
    axs=None,
    plot_legend: bool = True,
    exclude_xy_plane_object_list: list[SimulationObject] = [],
    exclude_yz_plane_object_list: list[SimulationObject] = [],
    exclude_xz_plane_object_list: list[SimulationObject] = [],
):
    # add pml to exclude lists
    for o in objects.objects:
        if not isinstance(o, PerfectlyMatchedLayer):
            continue
        if o.axis == 0:
            exclude_yz_plane_object_list.append(o)
        elif o.axis == 1:
            exclude_xz_plane_object_list.append(o)
        elif o.axis == 2:
            exclude_xy_plane_object_list.append(o)
    # add volume to exclude list
    volume = objects.volume
    exclude_object_list.append(volume)

    object_list = [o for o in objects.objects if o not in exclude_object_list]
    if axs is None:
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    else:
        fig = None
    resolution = config.resolution / 1.0e-6  # Convert to µm
    
    # get a color map
    colored_objects: list[SimulationObject] = [
        o for o in object_list if o.color is not None
    ]

    if plot_legend:
        handles = []
        used_lists = []
        for o in colored_objects:
            print_single = False
            for o2 in colored_objects:
                if o.__class__ == o2.__class__:
                    if o.color != o2.color:
                        print_single = True
                    if not o.name.startswith("Object"):
                        print_single = True
            label = o.__class__.__name__ if o.name.startswith("Object") else o.name
            patch = Patch(color=o.color, label=label)
            if print_single:
                handles.append(patch)
            else:
                if o.__class__.__name__ not in used_lists:
                    used_lists.append(o.__class__.__name__)
                    handles.append(patch)
        
        plt.legend(
            handles=handles,
            loc="upper right",
            bbox_to_anchor=(1.75, 0.75),
            frameon=False,
        )

    # Plot each object on the corresponding subplot
    for obj in colored_objects:
        slices = obj.grid_slice_tuple
        color = obj.color

        # XY plane at Z center
        if (
            exclude_xy_plane_object_list is None
            or obj not in exclude_xy_plane_object_list
        ):
            axs[0].add_patch(
                Rectangle(
                    (slices[0][0] * resolution, slices[1][0] * resolution),
                    (slices[0][1] - slices[0][0]) * resolution,
                    (slices[1][1] - slices[1][0]) * resolution,
                    color=color,
                    alpha=0.5,
                )
            )

        # XZ plane at Y center
        if (
            exclude_xz_plane_object_list is None
            or obj not in exclude_xz_plane_object_list
        ):
            axs[1].add_patch(
                Rectangle(
                    (slices[0][0] * resolution, slices[2][0] * resolution),
                    (slices[0][1] - slices[0][0]) * resolution,
                    (slices[2][1] - slices[2][0]) * resolution,
                    color=color,
                    alpha=0.5,
                )
            )
        
        # YZ plane at X center
        if (
            exclude_yz_plane_object_list is None
            or obj not in exclude_yz_plane_object_list
        ):
            axs[2].add_patch(
                Rectangle(
                    (slices[1][0] * resolution, slices[2][0] * resolution),
                    (slices[1][1] - slices[1][0]) * resolution,
                    (slices[2][1] - slices[2][0]) * resolution,
                    color=color,
                    alpha=0.5,
                )
            )


    axs[0].set_title("XY plane")
    axs[0].set_xlabel("X axis (µm)")
    axs[0].set_ylabel("Y axis (µm)")
    axs[0].set_xlim([0, volume.grid_shape[0] * resolution])
    axs[0].set_ylim([0, volume.grid_shape[1] * resolution])
    
    axs[1].set_title("XZ plane")
    axs[1].set_xlabel("X axis (µm)")
    axs[1].set_ylabel("Z axis (µm)")
    axs[1].set_xlim([0, volume.grid_shape[0] * resolution])
    axs[1].set_ylim([0, volume.grid_shape[2] * resolution])
    
    axs[2].set_title("YZ plane")
    axs[2].set_xlabel("Y axis (µm)")
    axs[2].set_ylabel("Z axis (µm)")
    axs[2].set_xlim([0, volume.grid_shape[1] * resolution])
    axs[2].set_ylim([0, volume.grid_shape[2] * resolution])

    
    # Adjust the plots for better visualization
    for ax in axs:
        ax.set_aspect("equal")
        ax.grid(True)

    if filename is not None:
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()
    return plt.gcf() if fig is None else fig