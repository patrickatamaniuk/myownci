class Ability
  include CanCan::Ability
 
  def initialize(user)
    user ||= User.new # guest user

    if user.role? :admin
      can :manage, :all
    elsif user.role? :committer
      can :read, [Requests, Jobs]
    end
  end
end
