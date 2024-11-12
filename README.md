# EC2 CloudWatch 告警自动化管理

这个 CloudFormation 模板部署了一个自动化解决方案，用于基于实例标签管理 EC2 实例的 CloudWatch 告警。它可以在 EC2 实例启动或终止时自动创建和删除 CloudWatch 告警。

## 功能特点

- 自动为带有指定标签的 EC2 实例创建 CloudWatch 告警
- 支持多种 CloudWatch 指标（StatusCheckFailed、CPUUtilization）
- 根据 EC2 实例生命周期动态管理告警
- 可配置的告警参数（阈值、评估周期等）
- 与 SNS 集成实现告警通知

## 前提条件

- AWS 账户
- 用于告警通知的现有 SNS 主题
- 带有适当标签的 EC2 实例
- 创建 CloudFormation 堆栈所需的 IAM 权限

## 架构

![Architecture Overview](https://github.com/jas0n1iu/AutoCreateEC2AlarmViaTag/blob/main/images/Architecture.png)

该解决方案包含以下组件：

1. **Lambda 函数**: 管理 CloudWatch 告警的创建和删除
2. **EventBridge 规则**: 监控 EC2 实例状态变化
3. **IAM 角色**: 为 Lambda 函数提供必要权限
4. **自定义资源**: 为现有实例初始化告警

## 参数配置

### 基础配置

- **TagKey**: 用于筛选 EC2 实例的标签键（默认："Environment"，需要修改为实际的Tag Key）
- **TagValue**: 用于筛选 EC2 实例的标签值（默认："Production"， 需要修改为实际的Tag Value）
- **AlertSNSTopicArn**: 现有 SNS 主题的 ARN

### CloudWatch 指标配置

- **MetricName**: 监控的指标（StatusCheckFailed 或 CPUUtilization）
- **Statistic**: 统计方法（Maximum、Minimum、Average、Sum、SampleCount）
- **Period**: 指标评估的时间周期
- **EvaluationPeriods**: 评估周期数
- **DatapointsToAlarm**: 触发告警所需的数据点数量
- **ComparisonOperator**: 阈值比较方法
- **Threshold**: 告警阈值

## 部署步骤

点击以下Launch Stack图标以创建Cloudformation 堆栈

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?#/stacks/create/review?templateURL=https://s3.us-west-2.amazonaws.com/examplelabs.net/template/cf-TAG-to-create-alarm.yaml&stackName=EC2Tag2Alarm)

## 使用说明

1. 为 EC2 实例添加指定的 TagKey 和 TagValue
2. 解决方案将自动为匹配的实例创建 CloudWatch 告警
3. 当实例终止时，其告警会自动删除
4. 告警将触发通知到指定的 SNS 主题