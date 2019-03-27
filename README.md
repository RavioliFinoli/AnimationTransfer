# Animation Transfer Tool for Maya
A tool that transfers animation from one skeleton to another.

## Table of Contents
[Notes](#notes)  
[Installation](#installation)  
[Usage](#usage)  
 [Transfer Tab](#transfer)  
 [Settings Tab](#settings)  
  

<a name="notes"/>

## Notes
  * **Requires the bindpose of both skeletons to be available at frame 0!**
  * Takes differences in joint orientation into account.
  * Allows user defined frame steps, as well as the option to apply an Euler filter to the result.
  * *Currently* only supports skeletons with the same number of joints.
  * The script only takes joint rotations into account (and root translation if desired).

<a name="installation"/>

## Installation
  * Copy AnimationTransfer.py and animation_transfer.ui to your maya scripts folder (../Documents/maya/VERSION/scripts on Windows)
  * Create a python script in Maya with the following:
   ```python
   import AnimationTransfer
   reload(AnimationTransfer)
   AnimationTransfer.run()
   ```
  * Run that script to open the tool (you probably want to save it to a shelf)

<a name="usage"/>

## Usage

<a name="transfer"/>

### Transfer tab 

![](https://i.imgur.com/A0yCmMX.png "Transfer Tab")
  * **Load Source/Target from Root**: Clear the list and loads the selected joint and its children. (You'll generally want to select the skeleton root)
  * **Load Source/Target from Selection**: Adds the current selection to the lists. Duplicates are ignored.
  * The listed joints can be reordered in case of joint mismatch by dragging/dropping them inside the lists.
  * **Transfer**: Starts the transfer. Note that Maya may become unresponsive during the transfer, though progress should be reflected in the progress bar that is shown during transfer.

<a name="settings"/>

### Settings tab

![](https://i.imgur.com/sXXDmez.png "Settings Tab")
  * **Transfer Range**: The range of frames to transfer. Currently supports time slider and time range. (Let me know if selection is something you'd want in this tool)
  * **Transfer every X frames**: Frame step size of transfer.
  * **Apply Euler Filter**: Whether to apply an Euler filter to the target's curves after transfer. Recommended if step size is greater than one.
  * **Transfer Root Translation**: Whether to transfer the translation of source root to target root. Note that this grabs the real root of each skeleton, not neccessarily the skeleton hierarchy roots.

