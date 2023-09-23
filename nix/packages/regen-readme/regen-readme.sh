# shellcheck shell=bash

# There is only one kind of command recognized by the template function:
#
# ```regen-readme
# command
# ```
#
# The template function will execute the command and replace the command
# with the command prefixed by "$ " followed by the output of the command.
function template() {
  local -n lines=$1
  local -i i=0
  while ((i < ${#lines[@]})); do
    if [[ ${lines[$i]} == '```regen-readme' ]]; then
      # Consume the start of the regen-readme block.
      echo '```console'
      ((i += 1))

      # Assert that we have more lines.
      if ((i >= ${#lines[@]})); then
        echo "Unexpected end of file while in regen-readme block: expected command."
        exit 1
      fi

      # Consume the command line.
      cmd="${lines[$i]}"
      echo "$ $cmd"
      ((i += 1))

      # Execute the command, capturing the output and filtering out the "warning: Git tree ... is dirty" message.
      output=$(eval "$cmd" 2>&1 | grep -v 'warning: Git tree')
      echo "$output"
      # NOTE: We don't increment $i here because we are *generating* lines.

      # Assert that we have more lines.
      if ((i >= ${#lines[@]})); then
        echo "Unexpected end of file while in regen-readme block: expected end of block."
        exit 1
      fi

      # Assert that the next line is the end of the block.
      if [[ ${lines[$i]} != '```' ]]; then
        echo "Expected end of regen-readme block, but got: ${lines[$i]}"
        exit 1
      fi

      # Fall through and consume the end of the block.
    fi
    # Consume the line.
    echo "${lines[$i]}"
    ((i += 1))
  done
}

function usage() {
  echo "Usage: $0 <template-file>"
  echo "  <template-file> is the path to the template file."
}

function main() {
  if [[ $# -ne 1 ]]; then
    usage
    exit 1
  fi

  local template_file="$1"

  # Check that the template file exists.
  if [[ ! -f $template_file ]]; then
    echo "Template file not found: $template_file"
    exit 1
  fi

  # Check that the template file is readable.
  if [[ ! -r $template_file ]]; then
    echo "Template file is not readable: $template_file"
    exit 1
  fi

  # Read the template file into an array.
  # Shellcheck doesn't know how to handle namerefs.
  # shellcheck disable=SC2034
  readarray -t template_lines <"$template_file"

  # Print the template file with the regen-readme blocks replaced.
  template template_lines
}

main "$@"
