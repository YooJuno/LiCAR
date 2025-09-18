// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from my_interfaces:msg/StartSignal.idl
// generated code does not contain a copyright notice

#include "my_interfaces/msg/detail/start_signal__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_my_interfaces
const rosidl_type_hash_t *
my_interfaces__msg__StartSignal__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x95, 0xbc, 0xe1, 0xdd, 0x51, 0x86, 0x8e, 0x6e,
      0xcb, 0x4e, 0x33, 0x0f, 0x5a, 0x04, 0x28, 0x6a,
      0x33, 0xd0, 0xdc, 0x72, 0xd9, 0xc3, 0x6d, 0xbe,
      0x7d, 0xaa, 0x20, 0x43, 0xdb, 0xb2, 0x33, 0x25,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char my_interfaces__msg__StartSignal__TYPE_NAME[] = "my_interfaces/msg/StartSignal";

// Define type names, field names, and default values
static char my_interfaces__msg__StartSignal__FIELD_NAME__start[] = "start";

static rosidl_runtime_c__type_description__Field my_interfaces__msg__StartSignal__FIELDS[] = {
  {
    {my_interfaces__msg__StartSignal__FIELD_NAME__start, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
my_interfaces__msg__StartSignal__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {my_interfaces__msg__StartSignal__TYPE_NAME, 29, 29},
      {my_interfaces__msg__StartSignal__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "bool start";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
my_interfaces__msg__StartSignal__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {my_interfaces__msg__StartSignal__TYPE_NAME, 29, 29},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 10, 10},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
my_interfaces__msg__StartSignal__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *my_interfaces__msg__StartSignal__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
