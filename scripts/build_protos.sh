SRC_DIR=$PWD/protos/src
DST_DIR=$PWD/src/tuneflow_py/models/protos
mkdir -p $DST_DIR
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/song.proto