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
The value of `MSG_ID` is a decimal (ie: base-10) number, encoded (using `$CHR()`) in a single byte as an ASCII character (ie: a message with an id of `15` will be encoded as an ASCII 'shift in' character (`SI`)).

The entire message will be encoded and decoded using the `$ENCODE()` and `$DECODE()` AS instructions respectively.

Contents of `data` fields is message specific and will be described later in this document.

## Message types

The following named message types have been mapped onto numeric IDs:

| Message          | ID |
|------------------|---:|
| `JOINT_POSITION` | 10 |
| `JOINT_TRAJ_PT`  | 11 |
| `STATUS`         | 13 |

## Message definitions

The following sections show the structure of all messages that can be legally send and received by clients and servers.

Note: only the message specific fields are documented in these sections. All message types do however include the 'header' fields (`MSG_START0`, `MSG_START1`, `MSG_LEN` and `MSG_ID`) at the start and the footer (`MSG_END`) at the end of the message.

For an explanation of the contents of the standard fields, see the *Message format* section.

### JOINT_POSITION

This message is used to encode the *joint space pose* of the robot at a specific point in time.

Message type: *publication*

Message ID: 10

| Field        | Value | Description                               |
|--------------|------:|-------------------------------------------|
| header       |     - | -                                         |
| `joint_0`    |       | Joint angle of the first joint (radians)  |
| `joint_1`    |       | Joint angle of the second joint (radians) |
| `joint_2`    |       | Joint angle of the third joint (radians)  |
| `joint_3`    |       | Joint angle of the fourth joint (radians) |
| `joint_4`    |       | Joint angle of the fifth joint (radians)  |
| `joint_5`    |       | Joint angle of the sixth joint (radians)  |
| footer       |     - | -                                         |

### TRAJ_PT

This message is used to enqueue a new *joint space pose* for the robot to move to as soon as it has processed any earlier enqueued poses.

Message type: *service request*

Message ID: 11

| Field        | Value | Description                                 |
|--------------|------:|---------------------------------------------|
| header       |     - | -                                           |
| `seq_num`    |00->99 | ID of this trajectory point                 |
| `speed`      |       | Speed for all following movements (`(0; 100]`) |
| `accuracy`   |       | Accuracy for all following movements (millimeters) |
| `accelerate` |       | Accel. for all following movements (`(0; 100]`) |
| `decelerate` |       | Decel. for all following movements (`(0; 100]`) |
| `break`      |       | Break continuous motion planning after reaching this trajectory point, 0 or 1 |
| `joint_0`    |       | Joint angle of the first joint (radians)    |
| `joint_1`    |       | Joint angle of the second joint (radians)   |
| `joint_2`    |       | Joint angle of the third joint (radians)    |
| `joint_3`    |       | Joint angle of the fourth joint (radians)   |
| `joint_4`    |       | Joint angle of the fifth joint (radians)    |
| `joint_5`    |       | Joint angle of the sixth joint (radians)    |
| `duration`   |       | Total time for this trajectory segment (ms) |
| footer       |     - | -                                           |

#### Example

```
0x02|0x01|45|11|03|10|400|100|100|0|-40|20|-50|0|10|100|0x03
```

#### TODO

 * document what happens for trajectories with `seq_num > 99`
 * document whether `speed` or `duration` is used when both are specified
 * document *how* `duration` is used when specified
 * describe mapping of `speed`, `accuracy`, `accelerate`, `decelerate` and `break` on AS motion primitives/params
 * document the reply send back by the server upon reception of this message
 * flesh out example

### STATUS

This message encodes the overall status of the robot controller: whether motion is possible, drives are powered, in which mode the controller is (manual, auto), etc.

Message type: *publication*

Message ID: 13

| Field             | Value | Description                                 |
|-------------------|------:|---------------------------------------------|
| header            |     - | -                                           |
| `drives_powered`  |       | Whether the robot drives are powered on     |
| `e_stopped`       |       | Whether the robot is e-stopped              |
| `error_code`      |       | Currently active error code (numeric ID)    |
| `in_error`        |       | Whether the robot is currently in an error state |
| `in_motion`       |       | Whether the robot is currently executing a motion |
| `mode`            |       | Current controller mode as defined in ISO 10218-1 (`UNKNOWN`, `MANUAL` or `AUTO`) |
| `motion_possible` |       | Whether the robot can execute motions       |
| footer            |     - | -                                           |

#### TODO

 * document valid values for `mode` field
 * provide example mapping of message fields to Kawasaki controller status fields

## Examples

TODO.
