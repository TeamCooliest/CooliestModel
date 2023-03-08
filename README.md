# TeamCooliest

## File Structure

Subject to change.
It may be better to group parallel CFD and model cases than separate them in the `data` directory.

- data
  - CFD
  - model

- src
  - CFD
  - GUI
  - model

## Branch Organization

- main (runnable use case)
  - develop (merge subtask developments and test)
    - develop-gui
    - develop-cfd
    - develop-model

Individual user branches can stem from develop-{subtask}