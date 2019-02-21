# Animation Transfer Tool for Maya
A tool that transfers animation from one skeleton to another.

## Table of Contents
[Notes](#notes)

<a name="notes"/>

## Notes
  * Takes differences in joint orientation into account.
  * Allows user defined frame steps, as well as the option to apply an Euler filter to the result.
  * *Currently* only supports skeletons with the same number of joints.
  * The script only takes joint rotations into account (and root translation if desired).

## Installation
  * Copy AnimationTransfer.py and animation_transfer.ui to your maya scripts folder (../Documents/maya/VERSION/scripts on Windows)
  * Create a python script in Maya with the following:
   ```python
   import AnimationTransfer
   reload(AnimationTransfer)
   AnimationTransfer.run()
   ```
  * Run that script to open the tool (you probably want to save it to a shelf)

## Usage
### Transfer tab
The *Load Source/Target from Root* buttons loads the selected joint and its children. (You'll generally want to select the skeleton root)
The *Load Source/Target from Selection* add the current selection to the lists. Duplicates are ignored.
The listed joints can be reordered in case of joint mismatch by dragging/dropping them inside the lists.

### Settings tab
  * **Transfer Range**: The range of frames to transfer. Currently supports time slider and time range. (Let me know if selection is something you'd want in this tool)
  * **Transfer every X frames**: Frame step size of transfer.
  * **Apply Euler Filter**: Whether to apply an Euler filter to the target's curves after transfer. Recommended if step size is greater than one.
  * **Transfer Root Translation**: Whether to transfer the translation of source root to target root. Note that this grabs the real root of each skeleton, not neccessarily the skeleton hierarchy roots.
![alt text](https://i.imgur.com/4PgV9fD.png "Script in action")
