class UsersController < ApplicationController
  helper HabtmCheckboxes
  check_authorization
  before_filter :get_user, :only => [:index, :new, :edit]
  before_filter :accessible_roles, :only => [:new, :edit, :show, :update, :create]
  load_and_authorize_resource :only => [:show,:new,:destroy,:edit,:update]
#  before_filter :authenticate_user!

  def index
    @users = User.all
    authorize! :read, @users
  end

  def new
    respond_to do |format|
      format.html
    end
  end

  def show
    respond_to do |format|
      format.html      
    end
 
  rescue ActiveRecord::RecordNotFound
    respond_to_not_found(:json, :xml, :html)
  end

  def edit
    respond_to do |format|
      format.html
    end
 
  rescue ActiveRecord::RecordNotFound
    respond_to_not_found(:json, :xml, :html)
  end
 
  def destroy
    @user.destroy
    @user = nil 
    Rails.logger.info('redirecting....')
    respond_to do |format|
      format.html {
        redirect_to users_path
      }
    end
 
  rescue ActiveRecord::RecordNotFound
    respond_to_not_found(:json, :xml, :html)
  end
 
  # 
  def create
    authorize! :create, User
    @user = User.new(params[:user])
 
    if @user.save
      respond_to do |format|
        format.html { redirect_to :action => :index }
      end
    else
      respond_to do |format|
        format.html { render :action => :new, :status => :unprocessable_entity }
      end
    end
  end

  def update
    if params[:user][:password].blank?
      [:password,:password_confirmation,:current_password].collect{|p| params[:user].delete(p) }
    else
      @user.errors[:base] << "The password you entered is incorrect" unless @user.valid_password?(params[:user][:current_password])
    end
 
    respond_to do |format|
      if @user.errors[:base].empty? and @user.update_attributes(params[:user])
        flash[:notice] = "Your account has been updated"
        format.json { render :json => @user.to_json, :status => 200 }
        format.xml  { head :ok }
        format.html { render :action => :edit }
      else
        format.json { render :text => "Could not update user", :status => :unprocessable_entity } #placeholder
        format.xml  { render :xml => @user.errors, :status => :unprocessable_entity }
        format.html { render :action => :edit, :status => :unprocessable_entity }
      end
    end
 
  rescue ActiveRecord::RecordNotFound
    respond_to_not_found(:js, :xml, :html)
  end

  def accessible_roles
    @accessible_roles = Role.accessible_by(current_ability,:read)
  end

  def get_user
    @current_user = current_user
  end
end
