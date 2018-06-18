# Overview

Simple, text-based protocol to be used between the programs running on the Kawasaki controller and those on the PC.


## Message format

The basic message format is as follows:

```
MSG_START0|MSG_START1|MSG_LEN|MSG_ID|data|data|..|MSG_END
```

Where:

| Field        | Description                       |
|--------------|-----------------------------------|
| `MSG_START0` | ASCII 'start of text'    (`0x02`) |
| `MSG_START1` | ASCII 'start of heading' (`0x01`) |
| `MSG_LEN`    | Length (in bytes) of the rest of the message, including `MSG_END` |
| `MSG_ID`     | Base-10 numeric msg id            |
| data         | fields of the message             |
| `MSG_END`    | ASCII 'end of text'      (`0x03`) |


Fields are separated by the ASCII 'pipe' symbol (`|`, `0x7C`).

Fields `MSG_START0`, `MSG_START1`, `MSG_LEN`, `MSG_ID` and `MSG_END` are encoded using `$CHR()`.
In case of `MSG_LEN`, this means that the maximum total message length (ie: all data following, up to and including `MSG_END`) is 255 bytes.
The value of `MSG_ID` is a decimal (ie: base-10) number, encoded (using `$CHR()`) in a single byte as an ASCII character (ie: a message with an id of `15` will be encoded as an ASCII 'shift in').

The entire message will be encoded and decoded using `$ENCODE()` and `$DECODE()` respectively.

Contents of `data` fields is message specific and will be described later in this document.

## Message types

The following named message types have been mapped onto numeric IDs:

| Message          | ID |
|------------------|---:|
| `JOINT_POSITION` | 10 |
| `JOINT_TRAJ_PT`  | 11 |
| `STATUS`         | -  |

## Message definitions

The following sections show the structure of all messages that can be legally send and received by clients and servers.

Note: all message structures are shown complete, with start, length, id and end fields, but only the message specific fields are documented.
For an explanation of the contents of the standard fields, see the *Message format* section.

### JOINT_POSITION

This message is used to encode the *joint space pose* of the robot at a specific point in time.

Message type: *publication*

Message ID: 10

| Field        | Value | Description                                 |
|--------------|------:|---------------------------------------------|
| `MSG_START0` |  0x02 | -                                           |
| `MSG_START1` |  0x01 | -                                           |
| `MSG_LEN`    |       | -                                           |
| `MSG_ID`     |    10 | -                                           |
| `joint_0`    |       | Joint angle of the first joint, in radians  |
| `joint_1`    |       | Joint angle of the second joint, in radians |
| `joint_2`    |       | Joint angle of the third joint, in radians  |
| `joint_3`    |       | Joint angle of the fourth joint, in radians |
| `joint_4`    |       | Joint angle of the fifth joint, in radians  |
| `joint_5`    |       | Joint angle of the sixth joint, in radians  |
| `MSG_END`    |  0x03 | -                                           |

### TRAJ_PT

This message is used to enqueue a new *joint space pose* for the robot to move to as soon as it has processed any earlier enqueued poses.

Message type: *service request*

Message ID: 11

| Field        | Value | Description                                 |
|--------------|------:|---------------------------------------------|
| `MSG_START0` |  0x02 | -                                           |
| `MSG_START1` |  0x01 | -                                           |
| `MSG_LEN`    |       | -                                           |
| `MSG_ID`     |    11 | Value that points to type of movement, 11 for jmove |
| `seq_num`    |00->99 | Number of previously sent traj points       |
| `speed`      |       | Speed for all following movements, percentage between 0 and 100 |
| `accuracy`   |       | Accuracy for all following movements, in millimeters |  
| `accelerate` |       | Acceleration for all following movements, percentage between 0 and 100 | 
| `decelerate` |       | Deceleration for all following movements, percentage between 0 and 100 |
| `break`      |       | Break continous motion planning after reaching trajectory points, 1 or 0| 
| `joint_0`    |       | Joint angle of the first joint, in radians  |
| `joint_1`    |       | Joint angle of the second joint, in radians |
| `joint_2`    |       | Joint angle of the third joint, in radians  |
| `joint_3`    |       | Joint angle of the fourth joint, in radians |
| `joint_4`    |       | Joint angle of the fifth joint, in radians  |
| `joint_5`    |       | Joint angle of the sixth joint, in radians  |
| `MSG_END`    |  0x03 | -                                           |

??| `duration`   |       | Duration (in ms) to move to this point      |??

example: 
	0x02|0x01|45|11|03|10|400|100|100|0  |-40|20|-50|0|10|100|0x03

### STATUS

This message encodes the overall status of the robot controller: whether motion is possible, drives are powered, in which mode the controller is (manual, auto), etc.

Message type: *publication*

Message ID: 13

| Field             | Value | Description                                 |
|-------------------|------:|---------------------------------------------|
| `MSG_START0`      |  0x02 | -                                           |
| `MSG_START1`      |  0x01 | -                                           |
| `MSG_LEN`         |       | -                                           |
| `MSG_ID`          |       | -                                           |
| `drives_powered`  |       |  |
| `e_stopped`       |       |  |
| `error_code`      |       |  |
| `in_error`        |       |  |
| `in_motion`       |       |  |
| `mode`            |       |  |
| `motion_possible` |       |  |
| `MSG_END`         |  0x03 | -                                           |


## Examples

Text.
