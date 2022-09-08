#include <update_move_base_parameter_recovery/update_costmap_parameter_recovery.h>
#include <pluginlib/class_list_macros.h>
#include <actionlib/client/simple_action_client.h>

PLUGINLIB_EXPORT_CLASS(
    update_move_base_parameter_recovery::UpdateCostmapParameterRecovery,
    nav_core::RecoveryBehavior
)

namespace update_move_base_parameter_recovery
{
UpdateCostmapParameterRecovery::UpdateCostmapParameterRecovery():
    initialized_(false)
{
}

void UpdateCostmapParameterRecovery::initialize(
            std::string name,
            tf2_ros::Buffer*,
            costmap_2d::Costmap2DROS* global_costmap,
            costmap_2d::Costmap2DROS* local_costmap)
{
    if (not initialized_) {
        ros::NodeHandle private_nh("~/" + name);
        private_nh.param("parameter_name", parameter_name_, std::string("/move_base_node/local_costmap/inflation_radius"));
        ptr_dynamic_param_client_ = \
            std::shared_ptr<dynamic_reconfigure::Client<costmap_2d::Costmap2DConfig>>(
                    new dynamic_reconfigure::Client<costmap_2d::Costmap2DConfig>(parameter_name_)
                    );

        private_nh.param("timeout_duration", timeout_duration_, 5.0);
        private_nh.param("footprint_padding", footprint_padding_, 5.0);
        costmap_config_ = costmap_2d::Costmap2DConfig::__getDefault__();
        ROS_INFO_STREAM("Initialize a plugin \"" << name << "\"");
        initialized_ = true;
    } else {
        ROS_ERROR("You should not call initialize twice on this object, doing nothing");
    }
}

UpdateCostmapParameterRecovery::~UpdateCostmapParameterRecovery()
{
}

void UpdateCostmapParameterRecovery::runBehavior()
{
    if (not initialized_)
    {
        ROS_ERROR("This object must be initialized before runBehavior is called");
        return;
    }

    bool success = ptr_dynamic_param_client_->getCurrentConfiguration(costmap_config_, ros::Duration(timeout_duration_));
    if ( success ) {
        ptr_dynamic_param_client_->setConfiguration(costmap_config_);
        costmap_config_.footprint_padding = footprint_padding_;
        ROS_INFO_STREAM("Update parameter of \"" << parameter_name_ << "\".");
    } else {
        ROS_ERROR("Failed to get Current Configuration.");
    }
}

};
