FROM python:3-slim

ENV MHS_DIR="mhs-reference-implementation"

# This will always be cached by a docker build. You will need to run `docker build --no-cache` in order to get the
# latest version of pipenv.
RUN pip install pipenv

WORKDIR /usr/src/app

COPY common common

# The Pipfiles are copied separately, so they create their own layer which will be cached unless the Pipfile contents
# change. This prevents pipenv install from being run every time `docker build` is run and source files have changed.
WORKDIR $MHS_DIR
COPY $MHS_DIR/Pipfile* ./

# Not using the install --system flag to install packages to the system python installation.
#   See https://github.com/pypa/pipenv/pull/2762
# Using install --deploy to raise an error if the Pipfile.lock is not in sync with the Pipfile.
#   See https://docs.pipenv.org/en/latest/advanced/#using-pipenv-for-deployments
# Using install --ignore-pipefile to ignore the Pipfile and use Pipfile.lock to define packages.
RUN pipenv install --deploy --ignore-pipfile

# Copy application source. Kept as a separate layer from the Pipfiles, so we benefit from Docker's caching of layers.
COPY $MHS_DIR/ ./

ENTRYPOINT ["pipenv", "run", "mhs"]
