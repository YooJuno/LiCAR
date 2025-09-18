// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from my_interfaces:msg/StartSignal.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "my_interfaces/msg/start_signal.hpp"


#ifndef MY_INTERFACES__MSG__DETAIL__START_SIGNAL__BUILDER_HPP_
#define MY_INTERFACES__MSG__DETAIL__START_SIGNAL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "my_interfaces/msg/detail/start_signal__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace my_interfaces
{

namespace msg
{

namespace builder
{

class Init_StartSignal_start
{
public:
  Init_StartSignal_start()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::my_interfaces::msg::StartSignal start(::my_interfaces::msg::StartSignal::_start_type arg)
  {
    msg_.start = std::move(arg);
    return std::move(msg_);
  }

private:
  ::my_interfaces::msg::StartSignal msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::my_interfaces::msg::StartSignal>()
{
  return my_interfaces::msg::builder::Init_StartSignal_start();
}

}  // namespace my_interfaces

#endif  // MY_INTERFACES__MSG__DETAIL__START_SIGNAL__BUILDER_HPP_
