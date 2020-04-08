# ArUco generator for Gazebo

A small utility that converts an [`aruco_pose`-compatible map](https://github.com/CopterExpress/clever/blob/65d359b5c250f0ffdc20675c269ffe15899b4773/aruco_pose/README.md#aruco_map-nodelet) to a Gazebo world, creating all required ArUco models in the process.

## Usage

Clone this repository, then run

```bash
python3 ./generator.py <path/to/your/map.txt>
```

in the repository folder.

The script will generate all required ArUco marker models and place them in their respective folders (for example, ArUco marker 42 will be placed in `aruco_42` folder). Additionally, the script will generate the `aruco_world.world` file with references to the newly created models.

Move the marker folders to your `${HOME}/.gazebo/models` folder (create it if it's missing), then run

```bash
gazebo ./aruco_world.world
```

## Hacking

If you wish to add ArUco models to an existing .world file, copy your .world file to `templates/world_template.world`, open it in a text editor and add

```text
    $model_inclusions
```

where you wish the model inclusions to be placed. A good example would be after the `<world>` tag:

```xml
  <world name="default">
    $model_inclusions
    <include>
      <uri>model://sun</uri>
    </include>
    <!-- more descriptions -->
```

## Shortcomings

Since this is a quick and dirty way to generate worlds, there are multiple issues with it:

* Currently the generator expects to be executed from the source checkout directory;
* The generator is hardcoded to use the `DICT_4X4_1000` ArUco dictionary;
* The generator has no way of specifying the output directory for markers and .world files;
* The generator does not validate the map; as such, you can generate worlds from incorrect maps (with duplicate markers, for instance);
* In fact, if you try to generate several markers with the same ID but different sizes, only the marker with the last specified size will be generated;
* There are probably a lot more bugs here.

Consider this software a "proof of concept" quality.
