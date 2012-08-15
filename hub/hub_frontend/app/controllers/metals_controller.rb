class MetalsController < ApplicationController
  # GET /metals
  # GET /metals.json
  def index
    @metals = Metal.all

    respond_to do |format|
      format.html # index.html.erb
      format.json { render json: @metals }
    end
  end

  # GET /metals/1
  # GET /metals/1.json
  def show
    @metal = Metal.find(params[:id])

    respond_to do |format|
      format.html # show.html.erb
      format.json { render json: @metal }
    end
  end

  # DELETE /metals/1
  # DELETE /metals/1.json
  def destroy
    @metal = Metal.find(params[:id])
    @metal.destroy

    respond_to do |format|
      format.html { redirect_to metals_url }
      format.json { head :no_content }
    end
  end
end
