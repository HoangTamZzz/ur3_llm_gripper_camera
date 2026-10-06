#!/usr/bin/env python3
"""Spawn the configured UR3 workcell scene into Gazebo.

This file replaces the ad-hoc scene spawning logic from the original
ur3_llm_control project while keeping the same responsibility:
create the workspace/table, target zones and coloured cubes.

The new project is YAML-driven, so the scene geometry is shared with
MoveIt's PlanningScene and with the camera/perception stack.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from ur3_llm_control.scene_config import box_sdf, gazebo_boxes, load_scene


def _spawn_box(world_name: str, box) -> bool:
    """Spawn one configured BoxSpec using ros_gz_sim."""
    command = [
        "ros2", "run", "ros_gz_sim", "create",
        "-world", world_name,
        "-string", box_sdf(box),
        "-name", box.name,
        "-allow_renaming", "false",
        "-x", str(box.pose[0]),
        "-y", str(box.pose[1]),
        "-z", str(box.pose[2]),
        "-R", str(box.pose[3]),
        "-P", str(box.pose[4]),
        "-Y", str(box.pose[5]),
    ]
    result = subprocess.run(command, text=True)
    return result.returncode == 0


def spawn_scene(scene_file: str) -> int:
    """Spawn the configured scene in a deterministic order."""
    try:
        scene = load_scene(scene_file)
    except Exception as exc:
        print(f"[scene_spawner] Invalid scene file: {exc}", file=sys.stderr)
        return 2

    boxes = list(gazebo_boxes(scene))
    if not boxes:
        print("[scene_spawner] Scene contains no Gazebo entities.", file=sys.stderr)
        return 2

    print(
        f"[scene_spawner] Spawning {len(boxes)} entities in world "
        f"'{scene.world_name}'..."
    )

    # The table must exist before dynamic cubes are created.
    table = next((box for box in boxes if box.name == scene.table.name), None)
    dynamic_boxes = [box for box in boxes if box is not table]

    if table is not None:
        time.sleep(1.5)
        if not _spawn_box(scene.world_name, table):
            print(
                f"[scene_spawner] Failed to spawn table '{table.name}'.",
                file=sys.stderr,
            )
            return 1

    # Give Gazebo time to register the table collision before dropping cubes.
    time.sleep(1.0)

    for box in dynamic_boxes:
        if not _spawn_box(scene.world_name, box):
            print(
                f"[scene_spawner] Failed to spawn '{box.name}'.",
                file=sys.stderr,
            )
            return 1
        time.sleep(0.25)

    print("[scene_spawner] Scene spawn completed successfully.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Spawn the YAML-defined UR3e workcell scene."
    )
    parser.add_argument("--scene-file", required=True)
    args, _ = parser.parse_known_args()
    return spawn_scene(args.scene_file)


if __name__ == "__main__":
    raise SystemExit(main())
